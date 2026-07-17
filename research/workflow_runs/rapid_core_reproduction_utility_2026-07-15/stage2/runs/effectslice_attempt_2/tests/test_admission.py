import hashlib
import json
import sys
import unittest
from pathlib import Path


RUN_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RUN_ROOT / "src"))

from effectslice.admission import evaluate_full_eligibility, evaluate_slice_admission  # noqa: E402
from effectslice.models import (  # noqa: E402
    EligibilityInput,
    PairedDifference,
    SliceAdmissionInput,
    SliceCandidate,
)


MANIFEST_DIGEST = "a" * 64
ARTIFACT_DIGEST = "b" * 64


def paired_differences(values, seed_block_id):
    return tuple(
        PairedDifference(
            pair_id=f"{seed_block_id}:pair:{index:04d}",
            seed_block_id=seed_block_id,
            value=value,
        )
        for index, value in enumerate(values)
    )


def registry_digest(hypothesis_ids):
    payload = json.dumps(list(hypothesis_ids), separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def eligible_full():
    return evaluate_full_eligibility(
        EligibilityInput(
            full_effect_differences=paired_differences((0.8,) * 1000, "eligibility:001"),
            eligibility_seed_block_id="eligibility:001",
            difference_low=-1.0,
            difference_high=1.0,
            alpha_F=0.01,
            delta_min=0.05,
            minimum_pairs=3,
            contracts_pass=True,
            guardrails_pass=True,
            manifest_digest=MANIFEST_DIGEST,
        )
    )


def candidate(atom_ids=("A", "B"), full_atom_ids=("A", "B", "C")):
    return SliceCandidate(
        atom_ids=atom_ids,
        full_atom_ids=full_atom_ids,
        retained_scc_count=len(atom_ids),
        discovery_margin=0.02,
        normalized_cost=0.2,
        source_valid=True,
        executable=True,
        dependency_closed=True,
    )


def admission_input(**overrides):
    expected_hypotheses = (
        "baseline:B:non_admission",
        "baseline:clawtrace:matched_decision",
        "baseline:graph_of_skills:matched_decision",
        "baseline:skillrae:matched_decision",
        "control:permuted_margin:non_admission",
        "full:F:positive_effect",
        "neighbor:A",
        "neighbor:B",
        "slice:eq_lower",
        "slice:eq_upper",
    )
    values = {
        "eligibility": eligible_full(),
        "candidate": candidate(),
        "gap_differences": paired_differences((0.0,) * 1000, "confirmation:001"),
        "confirmation_seed_block_id": "confirmation:001",
        "discovery_seed_block_ids": ("discovery:001",),
        "minimum_confirmation_pairs": 3,
        "gap_low": -0.1,
        "gap_high": 0.1,
        "epsilon": 0.025,
        "alpha_C": 0.02,
        "discovery_queries": 2,
        "query_budget": 24,
        "neighbor_origin_map": (("A", "neighbor:A"), ("B", "neighbor:B")),
        "neighbor_failure_p_values": (("neighbor:A", 0.001), ("neighbor:B", 0.001)),
        "expected_confirmation_hypothesis_ids": expected_hypotheses,
        "sealed_p_values": (
            ("baseline:B:non_admission", 0.001),
            ("baseline:clawtrace:matched_decision", 0.001),
            ("baseline:graph_of_skills:matched_decision", 0.001),
            ("baseline:skillrae:matched_decision", 0.001),
            ("control:permuted_margin:non_admission", 0.001),
            ("full:F:positive_effect", 0.001),
            ("slice:eq_lower", 0.001),
            ("slice:eq_upper", 0.001),
        ),
        "confirmation_registry_digest": registry_digest(expected_hypotheses),
        "manifest_digest": MANIFEST_DIGEST,
        "artifact_digest": ARTIFACT_DIGEST,
        "contracts_pass": True,
        "guardrails_pass": True,
    }
    values.update(overrides)
    return SliceAdmissionInput(**values)


class FullEligibilityTest(unittest.TestCase):
    def test_rejects_duplicate_pair_identifiers(self):
        rows = paired_differences((0.8, 0.8, 0.8), "eligibility:001")
        duplicate_rows = (rows[0], rows[0], rows[2])

        with self.assertRaisesRegex(ValueError, "pair_id values must be unique"):
            evaluate_full_eligibility(
                EligibilityInput(
                    full_effect_differences=duplicate_rows,
                    eligibility_seed_block_id="eligibility:001",
                    difference_low=-1.0,
                    difference_high=1.0,
                    alpha_F=0.01,
                    delta_min=0.05,
                    minimum_pairs=3,
                    contracts_pass=True,
                    guardrails_pass=True,
                    manifest_digest=MANIFEST_DIGEST,
                )
            )

    def test_rejects_rows_outside_sealed_eligibility_block(self):
        with self.assertRaisesRegex(ValueError, "eligibility seed block mismatch"):
            evaluate_full_eligibility(
                EligibilityInput(
                    full_effect_differences=paired_differences(
                        (0.8, 0.8, 0.8), "eligibility:other"
                    ),
                    eligibility_seed_block_id="eligibility:001",
                    difference_low=-1.0,
                    difference_high=1.0,
                    alpha_F=0.01,
                    delta_min=0.05,
                    minimum_pairs=3,
                    contracts_pass=True,
                    guardrails_pass=True,
                    manifest_digest=MANIFEST_DIGEST,
                )
            )

    def test_rejects_non_finite_minimum_effect_threshold(self):
        for delta_min in (float("nan"), float("inf"), float("-inf")):
            with self.subTest(delta_min=delta_min):
                with self.assertRaisesRegex(ValueError, "delta_min must be finite"):
                    evaluate_full_eligibility(
                        EligibilityInput(
                            full_effect_differences=paired_differences(
                                (0.8,) * 1000, "eligibility:001"
                            ),
                            eligibility_seed_block_id="eligibility:001",
                            difference_low=-1.0,
                            difference_high=1.0,
                            alpha_F=0.01,
                            delta_min=delta_min,
                            minimum_pairs=3,
                            contracts_pass=True,
                            guardrails_pass=True,
                            manifest_digest=MANIFEST_DIGEST,
                        )
                    )

    def test_rejects_insufficient_paired_evidence(self):
        decision = evaluate_full_eligibility(
            EligibilityInput(
                full_effect_differences=paired_differences(
                    (0.8, 0.8), "eligibility:001"
                ),
                eligibility_seed_block_id="eligibility:001",
                difference_low=-1.0,
                difference_high=1.0,
                alpha_F=0.01,
                delta_min=0.05,
                minimum_pairs=3,
                contracts_pass=True,
                guardrails_pass=True,
                manifest_digest=MANIFEST_DIGEST,
            )
        )

        self.assertFalse(decision.admitted)
        self.assertEqual(decision.reason, "insufficient_paired_evidence")

    def test_rejects_full_artifact_without_sealed_positive_effect(self):
        decision = evaluate_full_eligibility(
            EligibilityInput(
                full_effect_differences=paired_differences(
                    (0.01,) * 1000, "eligibility:001"
                ),
                eligibility_seed_block_id="eligibility:001",
                difference_low=-1.0,
                difference_high=1.0,
                alpha_F=0.01,
                delta_min=0.05,
                minimum_pairs=3,
                contracts_pass=True,
                guardrails_pass=True,
                manifest_digest=MANIFEST_DIGEST,
            )
        )

        self.assertFalse(decision.admitted)
        self.assertEqual(decision.reason, "no_validated_beneficial_effect")


class SliceAdmissionTest(unittest.TestCase):
    def test_rejects_missing_equivalence_hypotheses(self):
        for sealed_p_values, missing_name in (
            ((), "slice:eq_lower"),
            (("slice:eq_lower", 0.001), "slice:eq_upper"),
        ):
            with self.subTest(sealed_p_values=sealed_p_values):
                if sealed_p_values and isinstance(sealed_p_values[0], str):
                    sealed_p_values = (sealed_p_values,)
                decision = evaluate_slice_admission(
                    admission_input(sealed_p_values=sealed_p_values)
                )

                self.assertFalse(decision.admitted)
                self.assertEqual(decision.reason, "incomplete_confirmation_family")
                self.assertEqual(decision.failed_hypothesis, missing_name)

    def test_rejects_empty_slice(self):
        decision = evaluate_slice_admission(admission_input(candidate=candidate(atom_ids=())))

        self.assertEqual(decision.reason, "empty_slice")

    def test_rejects_non_strict_subset(self):
        decision = evaluate_slice_admission(
            admission_input(candidate=candidate(atom_ids=("A", "B", "C")))
        )

        self.assertEqual(decision.reason, "not_strict_subset")

    def test_rejects_incomplete_neighbor_family(self):
        decision = evaluate_slice_admission(
            admission_input(neighbor_failure_p_values=(("neighbor:A", 0.001),))
        )

        self.assertEqual(decision.reason, "incomplete_neighbor_family")

    def test_rejects_neighbor_map_that_does_not_cover_retained_units(self):
        decision = evaluate_slice_admission(
            admission_input(neighbor_origin_map=(("A", "neighbor:A"),))
        )

        self.assertEqual(decision.reason, "incomplete_neighbor_family")
        self.assertEqual(decision.failed_hypothesis, "B")

    def test_allows_deduplicated_neighbor_for_multiple_origins(self):
        expected_hypotheses = tuple(
            hypothesis
            for hypothesis in admission_input().expected_confirmation_hypothesis_ids
            if hypothesis not in {"neighbor:A", "neighbor:B"}
        ) + ("neighbor:AB",)
        expected_hypotheses = tuple(sorted(expected_hypotheses))
        decision = evaluate_slice_admission(
            admission_input(
                neighbor_origin_map=(("A", "neighbor:AB"), ("B", "neighbor:AB")),
                neighbor_failure_p_values=(("neighbor:AB", 0.001),),
                expected_confirmation_hypothesis_ids=expected_hypotheses,
                confirmation_registry_digest=registry_digest(expected_hypotheses),
            )
        )

        self.assertTrue(decision.admitted)

    def test_rejects_unregistered_confirmation_hypothesis(self):
        decision = evaluate_slice_admission(
            admission_input(
                sealed_p_values=admission_input().sealed_p_values
                + (("unexpected:posthoc", 0.0001),)
            )
        )

        self.assertEqual(decision.reason, "confirmation_registry_mismatch")
        self.assertEqual(decision.failed_hypothesis, "unexpected:posthoc")

    def test_rejects_confirmation_rows_reused_from_discovery(self):
        with self.assertRaisesRegex(ValueError, "confirmation seed block must be disjoint"):
            evaluate_slice_admission(
                admission_input(
                    gap_differences=paired_differences((0.0,) * 10, "discovery:001"),
                    confirmation_seed_block_id="discovery:001",
                )
            )

    def test_rejects_non_finite_equivalence_margin(self):
        with self.assertRaisesRegex(ValueError, "epsilon must be finite and positive"):
            evaluate_slice_admission(admission_input(epsilon=float("nan")))

    def test_rejects_insufficient_query_budget(self):
        decision = evaluate_slice_admission(
            admission_input(
                discovery_queries=23,
                neighbor_failure_p_values=(),
            )
        )

        self.assertEqual(decision.reason, "insufficient_query_budget")

    def test_rejects_failed_confirmation_family(self):
        decision = evaluate_slice_admission(
            admission_input(
                sealed_p_values=tuple(
                    (name, 0.03 if name == "slice:eq_upper" else value)
                    for name, value in admission_input().sealed_p_values
                )
            )
        )

        self.assertEqual(decision.reason, "confirmation_family_failed")
        self.assertEqual(decision.failed_hypothesis, "slice:eq_upper")

    def test_admits_only_complete_passing_candidate(self):
        decision = evaluate_slice_admission(admission_input())

        self.assertTrue(decision.admitted)
        self.assertEqual(decision.reason, "admitted")
        self.assertLessEqual(decision.gap_interval[0], 0.0)
        self.assertGreaterEqual(decision.gap_interval[1], 0.0)
        self.assertEqual(decision.confirmation_registry_digest, registry_digest(
            admission_input().expected_confirmation_hypothesis_ids
        ))
        self.assertEqual(decision.confirmation_pair_ids[0], "confirmation:001:pair:0000")


if __name__ == "__main__":
    unittest.main()
