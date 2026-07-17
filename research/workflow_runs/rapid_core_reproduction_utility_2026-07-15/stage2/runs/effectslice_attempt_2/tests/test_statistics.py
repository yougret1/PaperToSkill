import math
import sys
import unittest
from pathlib import Path


RUN_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RUN_ROOT / "src"))

from effectslice.statistics import (  # noqa: E402
    clopper_pearson_upper_bound,
    exact_binomial_lower_tail_p_value,
    hoeffding_interval,
    hoeffding_lower_bound,
    holm_all_rejected,
    zero_violation_sample_size,
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


class ExactBinomialTest(unittest.TestCase):
    def test_zero_violation_p_value_matches_closed_form(self):
        actual = exact_binomial_lower_tail_p_value(
            violations=0,
            total=59,
            maximum_violation_rate=0.10,
        )

        self.assertAlmostEqual(actual, 0.9**59)

    def test_nonzero_violation_p_value_sums_lower_tail(self):
        actual = exact_binomial_lower_tail_p_value(
            violations=1,
            total=10,
            maximum_violation_rate=0.20,
        )
        expected = 0.8**10 + 10 * 0.2 * 0.8**9

        self.assertAlmostEqual(actual, expected)

    def test_rejects_invalid_counts_and_rates(self):
        invalid = (
            {"violations": -1, "total": 10, "maximum_violation_rate": 0.1},
            {"violations": 11, "total": 10, "maximum_violation_rate": 0.1},
            {"violations": 0, "total": 0, "maximum_violation_rate": 0.1},
            {"violations": True, "total": 10, "maximum_violation_rate": 0.1},
            {"violations": 0, "total": 10, "maximum_violation_rate": 1.0},
        )

        for kwargs in invalid:
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                exact_binomial_lower_tail_p_value(**kwargs)


class ClopperPearsonTest(unittest.TestCase):
    def test_zero_violation_upper_bound_matches_closed_form(self):
        actual = clopper_pearson_upper_bound(violations=0, total=21, alpha=0.01)

        self.assertAlmostEqual(actual, 1.0 - 0.01 ** (1.0 / 21.0), places=12)
        self.assertLess(actual, 0.20)

    def test_all_violations_have_unit_upper_bound(self):
        self.assertEqual(
            clopper_pearson_upper_bound(violations=7, total=7, alpha=0.05),
            1.0,
        )

    def test_upper_bound_increases_with_violation_count(self):
        bounds = [
            clopper_pearson_upper_bound(violations=count, total=20, alpha=0.05)
            for count in range(4)
        ]

        self.assertEqual(bounds, sorted(bounds))
        self.assertEqual(len(bounds), len(set(bounds)))

    def test_rejects_invalid_alpha(self):
        with self.assertRaisesRegex(ValueError, "alpha"):
            clopper_pearson_upper_bound(violations=0, total=10, alpha=0.0)


class SampleSizeTest(unittest.TestCase):
    def test_eligibility_needs_21_all_beneficial_pairs(self):
        self.assertEqual(
            zero_violation_sample_size(
                maximum_violation_rate=0.20,
                alpha=0.01,
                family_size=1,
            ),
            21,
        )

    def test_ten_hypothesis_confirmation_needs_59_pairs(self):
        self.assertEqual(
            zero_violation_sample_size(
                maximum_violation_rate=0.10,
                alpha=0.02,
                family_size=10,
            ),
            59,
        )

    def test_rejects_nonpositive_family_size(self):
        with self.assertRaisesRegex(ValueError, "family_size"):
            zero_violation_sample_size(0.10, 0.02, family_size=0)


if __name__ == "__main__":
    unittest.main()
