import math
import sys
import unittest
from pathlib import Path


RUN_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RUN_ROOT / "src"))

from effectslice.statistics import (  # noqa: E402
    hoeffding_interval,
    hoeffding_lower_bound,
    holm_all_rejected,
)


class HoeffdingStatisticsTest(unittest.TestCase):
    def test_lower_bound_matches_bounded_hoeffding_formula(self):
        values = [0.8] * 1000
        expected = 0.8 - 2.0 * math.sqrt(math.log(1.0 / 0.01) / (2.0 * 1000))

        actual = hoeffding_lower_bound(values, low=-1.0, high=1.0, alpha=0.01)

        self.assertAlmostEqual(actual, expected)

    def test_two_sided_interval_contains_sample_mean(self):
        lower, upper = hoeffding_interval([0.1, 0.2, 0.3], low=-1.0, high=1.0, alpha=0.05)

        self.assertLess(lower, 0.2)
        self.assertGreater(upper, 0.2)
        self.assertAlmostEqual(0.2 - lower, upper - 0.2)

    def test_rejects_empty_or_out_of_range_samples(self):
        with self.assertRaisesRegex(ValueError, "at least one"):
            hoeffding_lower_bound([], low=-1.0, high=1.0, alpha=0.01)
        with self.assertRaisesRegex(ValueError, "outside declared bounds"):
            hoeffding_interval([1.1], low=-1.0, high=1.0, alpha=0.05)


class HolmTest(unittest.TestCase):
    def test_all_rejected_when_each_sorted_p_value_clears_its_threshold(self):
        result = holm_all_rejected({"a": 0.001, "b": 0.009, "c": 0.015}, alpha=0.05)

        self.assertTrue(result.all_rejected)
        self.assertEqual(result.failed_hypothesis, None)

    def test_stops_at_first_failed_hypothesis(self):
        result = holm_all_rejected({"a": 0.001, "b": 0.03, "c": 0.031}, alpha=0.05)

        self.assertFalse(result.all_rejected)
        self.assertEqual(result.failed_hypothesis, "b")
        self.assertAlmostEqual(result.failed_threshold, 0.025)


if __name__ == "__main__":
    unittest.main()
