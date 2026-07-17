import hashlib
import json
import math
import sys
import unittest
from pathlib import Path


RUN_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RUN_ROOT / "src"))

from effectslice.pac_admission import (  # noqa: E402
    evaluate_full_eligibility,
    evaluate_sealed_confirmation,
)
from effectslice.pac_models import (  # noqa: E402
    BinaryObservation,
    ConfirmationHypothesisSpec,
    EligibilityInput,
    PairedDifference,
    SealedConfirmationInput,
    SliceCandidate,
    ViolationHypothesisEvidence,
)


MANIFEST_DIGEST = "a" * 64
ARTIFACT_DIGEST = "b" * 64
ELIGIBILITY_BLOCK = "eligibility:001"
CONFIRMATION_BLOCK = "confirmation:001"


def paired_differences(values, block=ELIGIBILITY_BLOCK):
    return tuple(
        PairedDifference(f"{block}:pair:{index:04d}", block, value)
        for index, value in enumerate(values)
    )


def confirmation_pair_ids(total=59):
    return tuple(f"{CONFIRMATION_BLOCK}:pair:{index:04d}" for index in range(total))


def observations(violations=(), total=59):
    violated = set(violations)
    return tuple(
        BinaryObservation(pair_id, CONFIRMATION_BLOCK, index in violated)
        for index, pair_id in enumerate(confirmation_pair_ids(total))
    )


def specs():
    return (
        ConfirmationHypothesisSpec("neighbor:A", 0.10),
        ConfirmationHypothesisSpec("neighbor:B", 0.10),
        ConfirmationHypothesisSpec("slice:preservation", 0.10),
    )


def evidence(overrides=None):
    overrides = overrides or {}
    return tuple(
        ViolationHypothesisEvidence(
            spec.hypothesis_id,
            spec.maximum_violation_rate,
            overrides.get(spec.hypothesis_id, observations()),
        )
        for spec in specs()
    )


def registry_digest(expected_specs=None, pair_ids=None):
    expected_specs = expected_specs or specs()
    pair_ids = pair_ids or confirmation_pair_ids()
    payload = {
        "hypotheses": [
            {
                "hypothesis_id": spec.hypothesis_id,
                "maximum_violation_rate": spec.maximum_violation_rate,
            }
            for spec in expected_specs
        ],
        "pair_ids": list(pair_ids),
    }
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def eligibility_input(**overrides):
    values = {
        "full_effect_differences": paired_differences((0.8,) * 21),
        "eligibility_seed_block_id": ELIGIBILITY_BLOCK,
        "alpha_F": 0.01,
        "delta_min": 0.05,
        "minimum_beneficial_prevalence": 0.80,
        "minimum_pairs": 21,
        "contracts_pass": True,
        "guardrails_pass": True,
        "manifest_digest": MANIFEST_DIGEST,
    }
    values.update(overrides)
    return EligibilityInput(**values)


def eligible_full():
    decision = evaluate_full_eligibility(eligibility_input())
    if not decision.admitted:
        raise AssertionError(f"invalid eligibility fixture: {decision}")
    return decision


def candidate(atom_ids=("A", "B"), full_atom_ids=("A", "B", "C")):
    return SliceCandidate(
        atom_ids=atom_ids,
        full_atom_ids=full_atom_ids,
        retained_scc_count=len(atom_ids),
        discovery_margin=0.02,
        source_valid=True,
        executable=True,
        dependency_closed=True,
    )


def confirmation_input(**overrides):
    expected_specs = specs()
    pair_ids = confirmation_pair_ids()
    values = {
        "eligibility": eligible_full(),
        "candidate": candidate(),
        "confirmation_seed_block_id": CONFIRMATION_BLOCK,
        "discovery_seed_block_ids": ("discovery:001",),
        "minimum_confirmation_pairs": 59,
        "alpha_C": 0.02,
        "discovery_queries": 2,
        "query_budget": 24,
        "neighbor_origin_map": (("A", "neighbor:A"), ("B", "neighbor:B")),
        "expected_confirmation_specs": expected_specs,
        "expected_confirmation_pair_ids": pair_ids,
        "confirmation_evidence": evidence(),
        "confirmation_registry_digest": registry_digest(expected_specs, pair_ids),
        "manifest_digest": MANIFEST_DIGEST,
        "artifact_digest": ARTIFACT_DIGEST,
        "contracts_pass": True,
        "guardrails_pass": True,
        "cost_constraints_pass": True,
    }
    values.update(overrides)
    return SealedConfirmationInput(**values)


class FullEligibilityTest(unittest.TestCase):
    def test_rejects_duplicate_or_wrong_block_pairs(self):
        rows = paired_differences((0.8,) * 21)
        with self.assertRaisesRegex(ValueError, "pair_id values must be unique"):
            evaluate_full_eligibility(
                eligibility_input(full_effect_differences=(rows[0], rows[0], *rows[2:]))
            )
        with self.assertRaisesRegex(ValueError, "eligibility seed block mismatch"):
            evaluate_full_eligibility(
                eligibility_input(full_effect_differences=paired_differences((0.8,) * 21, "other"))
            )

    def test_rejects_invalid_thresholds(self):
        for delta_min in (float("nan"), float("inf")):
            with self.subTest(delta_min=delta_min), self.assertRaisesRegex(
                ValueError, "delta_min"
            ):
                evaluate_full_eligibility(eligibility_input(delta_min=delta_min))
        for prevalence in (0.0, 1.0, float("nan")):
            with self.subTest(prevalence=prevalence), self.assertRaisesRegex(
                ValueError, "minimum_beneficial_prevalence"
            ):
                evaluate_full_eligibility(
                    eligibility_input(minimum_beneficial_prevalence=prevalence)
                )

    def test_rejects_insufficient_pairs_and_uncertified_prevalence(self):
        too_few = evaluate_full_eligibility(
            eligibility_input(full_effect_differences=paired_differences((0.8,) * 20))
        )
        one_failure = evaluate_full_eligibility(
            eligibility_input(full_effect_differences=paired_differences((0.8,) * 20 + (0.0,)))
        )

        self.assertEqual(too_few.reason, "insufficient_paired_evidence")
        self.assertEqual(one_failure.reason, "beneficial_prevalence_not_certified")
        self.assertEqual(one_failure.beneficial_count, 20)

    def test_accepts_exact_lower_bound_boundary(self):
        exact_lower = 0.01 ** (1.0 / 21.0)
        decision = evaluate_full_eligibility(
            eligibility_input(minimum_beneficial_prevalence=exact_lower)
        )

        self.assertTrue(decision.admitted)
        self.assertTrue(math.isclose(
            decision.beneficial_prevalence_lower_bound,
            exact_lower,
            rel_tol=0.0,
            abs_tol=1e-12,
        ))

    def test_contract_and_guardrail_failures_are_separate(self):
        self.assertEqual(
            evaluate_full_eligibility(eligibility_input(contracts_pass=False)).reason,
            "full_contract_failed",
        )
        self.assertEqual(
            evaluate_full_eligibility(eligibility_input(guardrails_pass=False)).reason,
            "full_guardrail_failed",
        )


class SealedConfirmationTest(unittest.TestCase):
    def test_rejects_empty_or_non_strict_slice(self):
        self.assertEqual(
            evaluate_sealed_confirmation(
                confirmation_input(candidate=candidate(atom_ids=()))
            ).reason,
            "empty_slice",
        )
        self.assertEqual(
            evaluate_sealed_confirmation(
                confirmation_input(candidate=candidate(atom_ids=("A", "B", "C")))
            ).reason,
            "not_strict_subset",
        )

    def test_requires_one_unique_neighbor_per_retained_atom(self):
        incomplete = evaluate_sealed_confirmation(
            confirmation_input(neighbor_origin_map=(("A", "neighbor:A"),))
        )
        self.assertEqual(incomplete.reason, "incomplete_neighbor_family")
        self.assertEqual(incomplete.failed_hypothesis, "B")
        with self.assertRaisesRegex(ValueError, "neighbor hypotheses must be unique"):
            evaluate_sealed_confirmation(
                confirmation_input(
                    neighbor_origin_map=(("A", "neighbor:A"), ("B", "neighbor:A"))
                )
            )

    def test_query_budget_failure_precedes_missing_evidence(self):
        decision = evaluate_sealed_confirmation(
            confirmation_input(discovery_queries=23, confirmation_evidence=())
        )
        self.assertEqual(decision.reason, "insufficient_query_budget")

    def test_rejects_reused_blocks_and_eligibility_pairs(self):
        with self.assertRaisesRegex(ValueError, "confirmation seed block must be disjoint"):
            evaluate_sealed_confirmation(
                confirmation_input(confirmation_seed_block_id="discovery:001")
            )

        overlap = eligible_full().pair_ids
        overlap_evidence = tuple(
            ViolationHypothesisEvidence(
                spec.hypothesis_id,
                spec.maximum_violation_rate,
                tuple(BinaryObservation(pair_id, CONFIRMATION_BLOCK, False) for pair_id in overlap),
            )
            for spec in specs()
        )
        with self.assertRaisesRegex(ValueError, "overlap eligibility"):
            evaluate_sealed_confirmation(
                confirmation_input(
                    minimum_confirmation_pairs=21,
                    expected_confirmation_pair_ids=overlap,
                    confirmation_evidence=overlap_evidence,
                    confirmation_registry_digest=registry_digest(specs(), overlap),
                )
            )

    def test_rejects_posthoc_hypothesis_or_threshold_change(self):
        unexpected = ViolationHypothesisEvidence(
            "unexpected:posthoc", 0.10, observations()
        )
        posthoc = evaluate_sealed_confirmation(
            confirmation_input(confirmation_evidence=evidence() + (unexpected,))
        )
        changed = tuple(
            ViolationHypothesisEvidence(
                item.hypothesis_id,
                0.20 if item.hypothesis_id == "slice:preservation" else item.maximum_violation_rate,
                item.observations,
            )
            for item in evidence()
        )
        threshold = evaluate_sealed_confirmation(
            confirmation_input(confirmation_evidence=changed)
        )

        self.assertEqual(posthoc.reason, "confirmation_registry_mismatch")
        self.assertEqual(posthoc.failed_hypothesis, "unexpected:posthoc")
        self.assertEqual(threshold.reason, "confirmation_registry_mismatch")
        self.assertEqual(threshold.failed_hypothesis, "slice:preservation")

    def test_rejects_incomplete_or_non_boolean_pair_outcomes(self):
        shortened = evaluate_sealed_confirmation(
            confirmation_input(
                confirmation_evidence=evidence({"slice:preservation": observations()[:-1]})
            )
        )
        self.assertEqual(shortened.reason, "confirmation_pair_coverage_mismatch")

        malformed = list(observations())
        malformed[0] = BinaryObservation(malformed[0].pair_id, CONFIRMATION_BLOCK, 1)
        with self.assertRaisesRegex(ValueError, "violated must be boolean"):
            evaluate_sealed_confirmation(
                confirmation_input(
                    confirmation_evidence=evidence({"slice:preservation": tuple(malformed)})
                )
            )

    def test_rejects_digest_mismatch_and_separate_hard_constraints(self):
        self.assertEqual(
            evaluate_sealed_confirmation(
                confirmation_input(confirmation_registry_digest="c" * 64)
            ).reason,
            "confirmation_registry_digest_mismatch",
        )
        self.assertEqual(
            evaluate_sealed_confirmation(
                confirmation_input(manifest_digest="c" * 64)
            ).reason,
            "manifest_digest_mismatch",
        )
        self.assertEqual(
            evaluate_sealed_confirmation(confirmation_input(contracts_pass=False)).reason,
            "slice_contract_failed",
        )
        self.assertEqual(
            evaluate_sealed_confirmation(confirmation_input(guardrails_pass=False)).reason,
            "slice_guardrail_failed",
        )
        self.assertEqual(
            evaluate_sealed_confirmation(
                confirmation_input(cost_constraints_pass=False)
            ).reason,
            "slice_cost_constraint_failed",
        )

    def test_rejects_failed_holm_family(self):
        decision = evaluate_sealed_confirmation(
            confirmation_input(
                confirmation_evidence=evidence(
                    {"slice:preservation": observations(violations=(0, 1))}
                )
            )
        )
        self.assertEqual(decision.reason, "confirmation_family_failed")
        self.assertEqual(decision.failed_hypothesis, "slice:preservation")

    def test_admits_complete_zero_violation_candidate(self):
        decision = evaluate_sealed_confirmation(confirmation_input())

        self.assertTrue(decision.admitted)
        self.assertEqual(decision.reason, "admitted")
        self.assertEqual(decision.confirmation_registry_digest, registry_digest())
        self.assertEqual(decision.confirmation_pair_ids, confirmation_pair_ids())
        self.assertEqual(len(decision.hypothesis_results), 3)
        self.assertTrue(all(result.rejected for result in decision.hypothesis_results))
        self.assertTrue(all(
            result.simultaneous_upper_bound < result.maximum_violation_rate
            for result in decision.hypothesis_results
        ))


if __name__ == "__main__":
    unittest.main()
