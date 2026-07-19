import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np


RUN_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RUN_ROOT / "src"))

from effectslice.snap_mfse_cases import (  # noqa: E402
    build_case_registry,
    compare_embedding,
    generate_case,
    paper_reference_embedding,
)


class SnapMFSECasesTest(unittest.TestCase):
    def test_reference_matches_paper_equations(self):
        counts = np.array(
            [
                [2.0, 1.0, 0.0, 0.0, 0.0, 1.0],
                [1.0, 3.0, 1.0, 0.0, 0.0, 0.0],
                [0.0, 1.0, 2.0, 1.0, 0.0, 0.0],
                [0.0, 0.0, 1.0, 3.0, 1.0, 0.0],
                [0.0, 0.0, 0.0, 1.0, 2.0, 1.0],
                [1.0, 0.0, 0.0, 0.0, 1.0, 3.0],
            ]
        )
        n_cells = counts.shape[0]
        idf = np.log(n_cells / (1.0 + np.count_nonzero(counts, axis=0)))
        x = counts * idf
        x /= np.linalg.norm(x, axis=1, keepdims=True)
        degree = x @ (x.T @ np.ones(n_cells)) - np.ones(n_cells)
        x_tilde = x / np.sqrt(degree)[:, None]
        expected_matrix = x_tilde @ x_tilde.T - np.diag(1.0 / degree)
        expected_values, expected_vectors = np.linalg.eigh(expected_matrix)
        order = np.argsort(expected_values)[::-1][:2]

        values, vectors = paper_reference_embedding(counts, 2)

        np.testing.assert_allclose(values, expected_values[order], atol=1e-12)
        expected_projector = expected_vectors[:, order] @ expected_vectors[:, order].T
        actual_projector = vectors @ vectors.T
        np.testing.assert_allclose(actual_projector, expected_projector, atol=1e-10)
        self.assertTrue(np.all(values[:-1] >= values[1:]))

    def test_comparison_is_sign_and_basis_invariant(self):
        counts = generate_case(
            {
                "case_id": "manual",
                "seed": 1701,
                "n_cells": 10,
                "n_features": 14,
                "n_components": 2,
                "cluster_count": 2,
            }
        )
        values, vectors = paper_reference_embedding(counts, 2)
        rotation = np.array([[0.0, -1.0], [1.0, 0.0]])

        equivalent = compare_embedding(
            counts,
            values,
            vectors @ rotation,
            expected_values=values,
            expected_vectors=vectors,
        )
        wrong = compare_embedding(
            counts,
            values + 0.25,
            vectors,
            expected_values=values,
            expected_vectors=vectors,
        )

        self.assertTrue(equivalent["passed"])
        self.assertLess(equivalent["projector_error"], 1e-10)
        self.assertFalse(wrong["passed"])
        self.assertFalse(wrong["eigenvalues_ok"])

    def test_reference_rejects_invalid_inputs(self):
        valid = np.array([[1.0, 0.0], [0.0, 1.0], [1.0, 1.0]])
        invalid = [
            np.array([1.0, 2.0]),
            np.array([[1.0, -1.0], [0.0, 1.0]]),
            np.array([[1.0, np.nan], [0.0, 1.0]]),
            np.array([[0.0, 0.0], [1.0, 1.0]]),
        ]
        for counts in invalid:
            with self.subTest(shape=counts.shape):
                with self.assertRaises(ValueError):
                    paper_reference_embedding(counts, 1)
        for components in (0, valid.shape[0]):
            with self.subTest(components=components):
                with self.assertRaises(ValueError):
                    paper_reference_embedding(valid, components)

    def test_case_registry_is_disjoint_deterministic_and_digest_bound(self):
        with tempfile.TemporaryDirectory() as first_tmp, tempfile.TemporaryDirectory() as second_tmp:
            first_path = Path(first_tmp) / "case_registry.json"
            second_path = Path(second_tmp) / "case_registry.json"
            first = build_case_registry(first_path)
            second = build_case_registry(second_path)
            first_bytes = first_path.read_bytes()
            second_bytes = second_path.read_bytes()

        self.assertEqual(first_bytes, second_bytes)
        self.assertEqual(first, second)
        self.assertEqual(
            {name: len(cases) for name, cases in first["blocks"].items()},
            {
                "development": 4,
                "eligibility": 21,
                "discovery": 16,
                "confirmation": 59,
                "confirmation_v2": 64,
                "confirmation_v4": 64,
            },
        )
        all_cases = [case for cases in first["blocks"].values() for case in cases]
        self.assertEqual(len({case["case_id"] for case in all_cases}), 228)
        self.assertEqual(len({case["seed"] for case in all_cases}), 228)
        for case in all_cases:
            counts = generate_case(case)
            self.assertEqual(
                case["counts_sha256"], hashlib.sha256(counts.tobytes()).hexdigest()
            )
            values, vectors = paper_reference_embedding(counts, case["n_components"])
            self.assertTrue(np.isfinite(values).all())
            self.assertEqual(vectors.shape, (case["n_cells"], case["n_components"]))
        reparsed = json.loads(first_bytes.decode("utf-8"))
        self.assertEqual(reparsed["registry_sha256"], first["registry_sha256"])


if __name__ == "__main__":
    unittest.main()
