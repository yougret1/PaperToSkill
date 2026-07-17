import json
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np


RUN_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RUN_ROOT / "src"))

from effectslice.toolformer_filter_cases import (  # noqa: E402
    BLOCK_SEEDS,
    build_case_registry,
    generate_case,
    paper_filter_api_calls,
    paper_weights,
)


class ToolformerFilterCasesTest(unittest.TestCase):
    def test_paper_weights_are_normalized_and_have_zero_tail(self):
        weights = paper_weights(8)
        expected = np.array([1.0, 0.8, 0.6, 0.4, 0.2, 0.0, 0.0, 0.0]) / 3.0

        np.testing.assert_allclose(weights, expected, rtol=0, atol=1e-15)
        self.assertAlmostEqual(float(weights.sum()), 1.0)

    def test_oracle_uses_min_counterfactual_and_inclusive_tie(self):
        with_result = np.array([[-1.0, -1.0], [-1.0, -1.0]])
        call_only = np.array([[-3.0, -3.0], [-1.5, -1.5]])
        no_call = np.array([[-2.0, -2.0], [-4.0, -4.0]])

        keep, margins = paper_filter_api_calls(
            with_result,
            call_only,
            no_call,
            tau_filter=0.5,
        )

        np.testing.assert_array_equal(keep, np.array([True, True]))
        np.testing.assert_allclose(margins, np.array([1.0, 0.5]), atol=1e-15)

    def test_zero_weight_tail_does_not_change_decision(self):
        base = np.array([[-1.0] * 8])
        changed = base.copy()
        changed[:, 5:] = -1000.0
        call_only = np.array([[-2.0] * 8])
        no_call = np.array([[-3.0] * 8])

        first = paper_filter_api_calls(base, call_only, no_call, 0.5)
        second = paper_filter_api_calls(changed, call_only, no_call, 0.5)

        np.testing.assert_array_equal(first[0], second[0])
        np.testing.assert_allclose(first[1], second[1], atol=1e-12)

    def test_oracle_rejects_invalid_inputs(self):
        valid = np.array([[-1.0, -2.0]])
        invalid_values = [
            np.array([-1.0, -2.0]),
            np.empty((0, 2)),
            np.array([[-1.0, np.nan]]),
            np.array([[-1.0, 0.1]]),
        ]
        for invalid in invalid_values:
            with self.subTest(shape=invalid.shape):
                with self.assertRaises(ValueError):
                    paper_filter_api_calls(invalid, valid, valid, 0.1)
        with self.assertRaises(ValueError):
            paper_filter_api_calls(valid, valid[:, :1], valid, 0.1)
        with self.assertRaises(ValueError):
            paper_filter_api_calls(valid, valid, valid, -0.1)

    def test_case_generation_is_deterministic_and_disjoint(self):
        self.assertEqual(
            {name: len(seeds) for name, seeds in BLOCK_SEEDS.items()},
            {
                "development": 4,
                "eligibility": 21,
                "discovery": 16,
                "confirmation": 59,
                "confirmation_v2": 64,
            },
        )
        all_seeds = [seed for seeds in BLOCK_SEEDS.values() for seed in seeds]
        self.assertEqual(len(all_seeds), len(set(all_seeds)))
        self.assertEqual(generate_case(all_seeds[0]), generate_case(all_seeds[0]))

    def test_frozen_cases_distinguish_uniform_weights(self):
        differences = 0
        for seed in [seed for seeds in BLOCK_SEEDS.values() for seed in seeds]:
            case = generate_case(seed)
            arrays = [np.asarray(case[key], dtype=float) for key in (
                "logp_with_result",
                "logp_call_only",
                "logp_no_call",
            )]
            keep, _ = paper_filter_api_calls(*arrays, case["tau_filter"])
            uniform = np.full(arrays[0].shape[1], 1.0 / arrays[0].shape[1])
            losses = [-(array * uniform).sum(axis=1) for array in arrays]
            wrong_margin = np.minimum(losses[1], losses[2]) - losses[0]
            wrong_keep = wrong_margin >= case["tau_filter"]
            differences += int(not np.array_equal(keep, wrong_keep))

        self.assertGreater(differences, 0)

    def test_confirmation_v2_has_diverse_shapes_decisions_and_boundaries(self):
        patterns = set()
        candidate_counts = set()
        has_inclusive_tie = False
        has_strict_rejection = False
        for seed in BLOCK_SEEDS["confirmation_v2"]:
            case = generate_case(seed)
            arrays = [
                np.asarray(case[key], dtype=float)
                for key in (
                    "logp_with_result",
                    "logp_call_only",
                    "logp_no_call",
                )
            ]
            keep, margins = paper_filter_api_calls(*arrays, case["tau_filter"])
            patterns.add(tuple(bool(value) for value in keep))
            candidate_counts.add(int(keep.size))
            has_inclusive_tie |= bool(
                np.any(np.isclose(margins, case["tau_filter"], rtol=0, atol=1e-12))
            )
            has_strict_rejection |= bool(np.any(margins < case["tau_filter"] - 1e-3))

        self.assertGreaterEqual(len(patterns), 6)
        self.assertGreaterEqual(len(candidate_counts), 3)
        self.assertTrue(has_inclusive_tie)
        self.assertTrue(has_strict_rejection)

    def test_registry_rebuild_is_byte_identical(self):
        with tempfile.TemporaryDirectory(dir=RUN_ROOT) as first, tempfile.TemporaryDirectory(
            dir=RUN_ROOT
        ) as second:
            first_path = Path(first) / "cases.json"
            second_path = Path(second) / "cases.json"
            build_case_registry(first_path)
            build_case_registry(second_path)
            first_bytes = first_path.read_bytes()
            second_bytes = second_path.read_bytes()
            first_registry = json.loads(first_path.read_text(encoding="utf-8"))

        self.assertEqual(first_bytes, second_bytes)
        self.assertEqual(
            {name: len(cases) for name, cases in first_registry["blocks"].items()},
            {
                "development": 4,
                "eligibility": 21,
                "discovery": 16,
                "confirmation": 59,
                "confirmation_v2": 64,
            },
        )


if __name__ == "__main__":
    unittest.main()
