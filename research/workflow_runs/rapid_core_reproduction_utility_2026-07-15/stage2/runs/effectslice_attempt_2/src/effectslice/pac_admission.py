from __future__ import annotations

import hashlib
import json
import math

from .pac_models import (
    ConfirmationHypothesisSpec,
    EligibilityDecision,
    EligibilityInput,
    HypothesisResult,
    PairedDifference,
    SealedConfirmationDecision,
    SealedConfirmationInput,
    ViolationHypothesisEvidence,
)
from .statistics import (
    clopper_pearson_upper_bound,
    exact_binomial_lower_tail_p_value,
    holm_all_rejected,
)


PRESERVATION_HYPOTHESIS_ID = "slice:preservation"


def _validate_digest(value: str, label: str) -> None:
    if len(value) != 64 or any(character not in "0123456789abcdef" for character in value):
        raise ValueError(f"{label} must be a lowercase SHA-256 digest")


def _validate_probability(value: float, label: str) -> float:
    probability = float(value)
    if not math.isfinite(probability) or not 0.0 < probability < 1.0:
        raise ValueError(f"{label} must be strictly between 0 and 1")
    return probability


def _validate_integer(value: int, label: str, *, allow_zero: bool) -> None:
    minimum = 0 if allow_zero else 1
    if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
        qualifier = "nonnegative" if allow_zero else "positive"
        raise ValueError(f"{label} must be a {qualifier} integer")


def _validate_paired_rows(
    rows: tuple[PairedDifference, ...],
    expected_seed_block_id: str,
    label: str,
) -> tuple[tuple[str, ...], tuple[float, ...]]:
    if not expected_seed_block_id:
        raise ValueError(f"{label} seed block must be nonempty")
    pair_ids = tuple(row.pair_id for row in rows)
    if any(not pair_id for pair_id in pair_ids):
        raise ValueError("pair_id values must be nonempty")
    if len(set(pair_ids)) != len(pair_ids):
        raise ValueError("pair_id values must be unique")
    if any(row.seed_block_id != expected_seed_block_id for row in rows):
        raise ValueError(f"{label} seed block mismatch")
    values = tuple(float(row.value) for row in rows)
    if any(not math.isfinite(value) for value in values):
        raise ValueError("paired differences must be finite")
    return pair_ids, values


def evaluate_full_eligibility(request: EligibilityInput) -> EligibilityDecision:
    _validate_integer(request.minimum_pairs, "minimum_pairs", allow_zero=False)
    if not math.isfinite(request.delta_min):
        raise ValueError("delta_min must be finite")
    alpha = _validate_probability(request.alpha_F, "alpha_F")
    minimum_prevalence = _validate_probability(
        request.minimum_beneficial_prevalence,
        "minimum_beneficial_prevalence",
    )
    _validate_digest(request.manifest_digest, "manifest_digest")
    pair_ids, values = _validate_paired_rows(
        request.full_effect_differences,
        request.eligibility_seed_block_id,
        "eligibility",
    )
    pair_count = len(values)
    if pair_count < request.minimum_pairs:
        return EligibilityDecision(
            False,
            "insufficient_paired_evidence",
            None,
            0,
            pair_count,
            request.manifest_digest,
            request.eligibility_seed_block_id,
            pair_ids,
        )
    if not request.contracts_pass:
        return EligibilityDecision(
            False,
            "full_contract_failed",
            None,
            0,
            pair_count,
            request.manifest_digest,
            request.eligibility_seed_block_id,
            pair_ids,
        )
    if not request.guardrails_pass:
        return EligibilityDecision(
            False,
            "full_guardrail_failed",
            None,
            0,
            pair_count,
            request.manifest_digest,
            request.eligibility_seed_block_id,
            pair_ids,
        )

    beneficial_count = sum(value >= request.delta_min for value in values)
    failure_count = pair_count - beneficial_count
    if failure_count == 0:
        lower_bound = alpha ** (1.0 / pair_count)
    else:
        lower_bound = 1.0 - clopper_pearson_upper_bound(
            failure_count,
            pair_count,
            alpha,
        )
    if lower_bound < minimum_prevalence and not math.isclose(
        lower_bound,
        minimum_prevalence,
        rel_tol=0.0,
        abs_tol=1e-15,
    ):
        reason = "beneficial_prevalence_not_certified"
        admitted = False
    else:
        reason = "eligible"
        admitted = True
    return EligibilityDecision(
        admitted,
        reason,
        lower_bound,
        beneficial_count,
        pair_count,
        request.manifest_digest,
        request.eligibility_seed_block_id,
        pair_ids,
    )


def confirmation_registry_digest(
    specs: tuple[ConfirmationHypothesisSpec, ...],
    pair_ids: tuple[str, ...],
) -> str:
    payload = {
        "hypotheses": [
            {
                "hypothesis_id": spec.hypothesis_id,
                "maximum_violation_rate": spec.maximum_violation_rate,
            }
            for spec in specs
        ],
        "pair_ids": list(pair_ids),
    }
    canonical = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _decision(
    request: SealedConfirmationInput,
    admitted: bool,
    reason: str,
    *,
    failed_hypothesis: str | None = None,
    results: tuple[HypothesisResult, ...] = (),
    pair_ids: tuple[str, ...] = (),
) -> SealedConfirmationDecision:
    return SealedConfirmationDecision(
        admitted,
        reason,
        failed_hypothesis,
        results,
        request.confirmation_registry_digest,
        request.manifest_digest,
        request.artifact_digest,
        pair_ids,
    )


def _validate_candidate(request: SealedConfirmationInput) -> SealedConfirmationDecision | None:
    candidate = request.candidate
    atom_ids = set(candidate.atom_ids)
    full_atom_ids = set(candidate.full_atom_ids)
    if not atom_ids:
        return _decision(request, False, "empty_slice")
    if len(atom_ids) != len(candidate.atom_ids) or len(full_atom_ids) != len(candidate.full_atom_ids):
        return _decision(request, False, "duplicate_atom_id")
    if candidate.atom_ids != tuple(sorted(atom_ids)):
        raise ValueError("candidate atom_ids must use canonical order")
    if candidate.full_atom_ids != tuple(sorted(full_atom_ids)):
        raise ValueError("candidate full_atom_ids must use canonical order")
    if candidate.retained_scc_count != len(atom_ids):
        raise ValueError("retained_scc_count must equal retained atom count")
    if not math.isfinite(candidate.discovery_margin):
        raise ValueError("discovery_margin must be finite")
    if not atom_ids.issubset(full_atom_ids):
        return _decision(request, False, "unknown_atom")
    if atom_ids == full_atom_ids:
        return _decision(request, False, "not_strict_subset")
    if not candidate.source_valid:
        return _decision(request, False, "invalid_source_atoms")
    if not candidate.executable:
        return _decision(request, False, "non_executable_slice")
    if not candidate.dependency_closed:
        return _decision(request, False, "dependency_not_closed")
    return None


def _validate_specs(
    specs: tuple[ConfirmationHypothesisSpec, ...],
) -> dict[str, float]:
    ids = tuple(spec.hypothesis_id for spec in specs)
    if not ids or any(not hypothesis_id for hypothesis_id in ids):
        raise ValueError("expected confirmation hypotheses must be nonempty")
    if ids != tuple(sorted(ids)) or len(set(ids)) != len(ids):
        raise ValueError("expected confirmation hypotheses must be unique and canonical")
    return {
        spec.hypothesis_id: _validate_probability(
            spec.maximum_violation_rate,
            f"maximum_violation_rate for {spec.hypothesis_id}",
        )
        for spec in specs
    }


def _validate_evidence_order(
    entries: tuple[ViolationHypothesisEvidence, ...],
) -> None:
    ids = tuple(entry.hypothesis_id for entry in entries)
    if any(not hypothesis_id for hypothesis_id in ids):
        raise ValueError("confirmation evidence hypothesis IDs must be nonempty")
    if len(set(ids)) != len(ids):
        raise ValueError("confirmation evidence hypothesis IDs must be unique")
    if ids != tuple(sorted(ids)):
        raise ValueError("confirmation evidence must use canonical order")


def evaluate_sealed_confirmation(
    request: SealedConfirmationInput,
) -> SealedConfirmationDecision:
    if not request.eligibility.admitted:
        return _decision(request, False, request.eligibility.reason)

    candidate_failure = _validate_candidate(request)
    if candidate_failure is not None:
        return candidate_failure
    if not request.contracts_pass:
        return _decision(request, False, "slice_contract_failed")
    if not request.guardrails_pass:
        return _decision(request, False, "slice_guardrail_failed")
    if not request.cost_constraints_pass:
        return _decision(request, False, "slice_cost_constraint_failed")

    _validate_integer(request.discovery_queries, "discovery_queries", allow_zero=True)
    _validate_integer(request.query_budget, "query_budget", allow_zero=False)
    _validate_integer(
        request.minimum_confirmation_pairs,
        "minimum_confirmation_pairs",
        allow_zero=False,
    )
    if request.discovery_queries + len(request.candidate.atom_ids) > request.query_budget:
        return _decision(request, False, "insufficient_query_budget")

    alpha = _validate_probability(request.alpha_C, "alpha_C")
    _validate_digest(request.manifest_digest, "manifest_digest")
    _validate_digest(request.artifact_digest, "artifact_digest")
    _validate_digest(request.confirmation_registry_digest, "confirmation_registry_digest")
    if request.eligibility.manifest_digest != request.manifest_digest:
        return _decision(request, False, "manifest_digest_mismatch")

    discovery_blocks = request.discovery_seed_block_ids
    if not discovery_blocks or any(not block for block in discovery_blocks):
        raise ValueError("discovery seed blocks must be nonempty")
    if discovery_blocks != tuple(sorted(discovery_blocks)) or len(set(discovery_blocks)) != len(discovery_blocks):
        raise ValueError("discovery seed blocks must be unique and canonical")
    forbidden_blocks = set(discovery_blocks)
    if request.eligibility.eligibility_seed_block_id:
        forbidden_blocks.add(request.eligibility.eligibility_seed_block_id)
    if not request.confirmation_seed_block_id:
        raise ValueError("confirmation seed block must be nonempty")
    if request.confirmation_seed_block_id in forbidden_blocks:
        raise ValueError("confirmation seed block must be disjoint from eligibility and discovery")

    expected_pair_ids = request.expected_confirmation_pair_ids
    if not expected_pair_ids or any(not pair_id for pair_id in expected_pair_ids):
        raise ValueError("expected confirmation pair IDs must be nonempty")
    if expected_pair_ids != tuple(sorted(expected_pair_ids)) or len(set(expected_pair_ids)) != len(expected_pair_ids):
        raise ValueError("expected confirmation pair IDs must be unique and canonical")
    if len(expected_pair_ids) < request.minimum_confirmation_pairs:
        return _decision(request, False, "insufficient_confirmation_pairs")
    overlap = set(expected_pair_ids) & set(request.eligibility.pair_ids)
    if overlap:
        raise ValueError(f"confirmation pair IDs overlap eligibility: {sorted(overlap)}")

    origin_map = request.neighbor_origin_map
    if origin_map != tuple(sorted(origin_map)):
        raise ValueError("neighbor_origin_map must use canonical order")
    origins = tuple(origin for origin, _ in origin_map)
    neighbor_hypotheses = tuple(hypothesis for _, hypothesis in origin_map)
    if len(set(origins)) != len(origins):
        raise ValueError("neighbor origins must be unique")
    if len(set(neighbor_hypotheses)) != len(neighbor_hypotheses):
        raise ValueError("neighbor hypotheses must be unique")
    if any(not origin or not hypothesis for origin, hypothesis in origin_map):
        raise ValueError("neighbor origin mappings must be nonempty")
    retained_atoms = set(request.candidate.atom_ids)
    missing_origins = sorted(retained_atoms - set(origins))
    unexpected_origins = sorted(set(origins) - retained_atoms)
    if missing_origins or unexpected_origins:
        failed = missing_origins[0] if missing_origins else unexpected_origins[0]
        return _decision(
            request,
            False,
            "incomplete_neighbor_family",
            failed_hypothesis=failed,
        )

    expected_rates = _validate_specs(request.expected_confirmation_specs)
    required_hypotheses = set(neighbor_hypotheses) | {PRESERVATION_HYPOTHESIS_ID}
    if set(expected_rates) != required_hypotheses:
        missing = sorted(required_hypotheses - set(expected_rates))
        unexpected = sorted(set(expected_rates) - required_hypotheses)
        failed = unexpected[0] if unexpected else missing[0]
        return _decision(
            request,
            False,
            "confirmation_registry_mismatch",
            failed_hypothesis=failed,
        )

    if request.confirmation_registry_digest != confirmation_registry_digest(
        request.expected_confirmation_specs,
        expected_pair_ids,
    ):
        return _decision(request, False, "confirmation_registry_digest_mismatch")

    _validate_evidence_order(request.confirmation_evidence)
    submitted = {entry.hypothesis_id: entry for entry in request.confirmation_evidence}
    missing = sorted(set(expected_rates) - set(submitted))
    unexpected = sorted(set(submitted) - set(expected_rates))
    if missing or unexpected:
        failed = unexpected[0] if unexpected else missing[0]
        return _decision(
            request,
            False,
            "confirmation_registry_mismatch",
            failed_hypothesis=failed,
        )
    for hypothesis_id, expected_rate in expected_rates.items():
        actual_rate = float(submitted[hypothesis_id].maximum_violation_rate)
        if actual_rate != expected_rate:
            return _decision(
                request,
                False,
                "confirmation_registry_mismatch",
                failed_hypothesis=hypothesis_id,
            )

    violation_counts: dict[str, int] = {}
    for hypothesis_id in sorted(submitted):
        rows = submitted[hypothesis_id].observations
        row_pair_ids = tuple(row.pair_id for row in rows)
        if any(row.seed_block_id != request.confirmation_seed_block_id for row in rows):
            raise ValueError("confirmation seed block mismatch")
        if any(not isinstance(row.violated, bool) for row in rows):
            raise ValueError("violated must be boolean")
        if row_pair_ids != expected_pair_ids:
            return _decision(
                request,
                False,
                "confirmation_pair_coverage_mismatch",
                failed_hypothesis=hypothesis_id,
            )
        violation_counts[hypothesis_id] = sum(row.violated for row in rows)

    p_values = {
        hypothesis_id: exact_binomial_lower_tail_p_value(
            violation_counts[hypothesis_id],
            len(expected_pair_ids),
            expected_rates[hypothesis_id],
        )
        for hypothesis_id in sorted(expected_rates)
    }
    holm = holm_all_rejected(p_values, alpha)
    sorted_p_values = sorted(p_values.items(), key=lambda item: (item[1], item[0]))
    thresholds: dict[str, float] = {}
    rejected: dict[str, bool] = {}
    still_rejecting = True
    total_hypotheses = len(sorted_p_values)
    for index, (hypothesis_id, p_value) in enumerate(sorted_p_values):
        threshold = alpha / (total_hypotheses - index)
        thresholds[hypothesis_id] = threshold
        still_rejecting = still_rejecting and p_value <= threshold
        rejected[hypothesis_id] = still_rejecting

    simultaneous_alpha = alpha / total_hypotheses
    results = tuple(
        HypothesisResult(
            hypothesis_id=hypothesis_id,
            maximum_violation_rate=expected_rates[hypothesis_id],
            violation_count=violation_counts[hypothesis_id],
            pair_count=len(expected_pair_ids),
            p_value=p_values[hypothesis_id],
            holm_threshold=thresholds[hypothesis_id],
            simultaneous_upper_bound=clopper_pearson_upper_bound(
                violation_counts[hypothesis_id],
                len(expected_pair_ids),
                simultaneous_alpha,
            ),
            rejected=rejected[hypothesis_id],
        )
        for hypothesis_id in sorted(expected_rates)
    )
    if not holm.all_rejected:
        return _decision(
            request,
            False,
            "confirmation_family_failed",
            failed_hypothesis=holm.failed_hypothesis,
            results=results,
            pair_ids=expected_pair_ids,
        )
    return _decision(
        request,
        True,
        "admitted",
        results=results,
        pair_ids=expected_pair_ids,
    )

