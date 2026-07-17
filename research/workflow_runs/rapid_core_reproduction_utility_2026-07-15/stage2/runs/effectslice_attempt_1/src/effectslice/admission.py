from __future__ import annotations

import hashlib
import json
import math

from .models import (
    EligibilityDecision,
    EligibilityInput,
    PairedDifference,
    SliceAdmissionDecision,
    SliceAdmissionInput,
)
from .statistics import hoeffding_interval, hoeffding_lower_bound, holm_all_rejected


REQUIRED_EQUIVALENCE_HYPOTHESES = ("slice:eq_lower", "slice:eq_upper")


def _validate_digest(value: str, label: str) -> None:
    if len(value) != 64 or any(character not in "0123456789abcdef" for character in value):
        raise ValueError(f"{label} must be a lowercase SHA-256 digest")


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
    return pair_ids, tuple(row.value for row in rows)


def _tuple_map(
    entries: tuple[tuple[str, float], ...], label: str
) -> dict[str, float]:
    names = tuple(name for name, _ in entries)
    if any(not name for name in names):
        raise ValueError(f"{label} hypothesis names must be nonempty")
    if len(set(names)) != len(names):
        raise ValueError(f"{label} hypothesis names must be unique")
    if names != tuple(sorted(names)):
        raise ValueError(f"{label} must use canonical hypothesis order")
    return dict(entries)


def _registry_digest(hypothesis_ids: tuple[str, ...]) -> str:
    payload = json.dumps(list(hypothesis_ids), separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _admission_decision(
    request: SliceAdmissionInput,
    admitted: bool,
    reason: str,
    gap_interval: tuple[float, float] | None = None,
    failed_hypothesis: str | None = None,
    pair_ids: tuple[str, ...] = (),
) -> SliceAdmissionDecision:
    return SliceAdmissionDecision(
        admitted=admitted,
        reason=reason,
        gap_interval=gap_interval,
        failed_hypothesis=failed_hypothesis,
        confirmation_registry_digest=request.confirmation_registry_digest,
        manifest_digest=request.manifest_digest,
        artifact_digest=request.artifact_digest,
        confirmation_pair_ids=pair_ids,
    )


def evaluate_full_eligibility(request: EligibilityInput) -> EligibilityDecision:
    if request.minimum_pairs < 1:
        raise ValueError("minimum_pairs must be positive")
    if not math.isfinite(request.delta_min):
        raise ValueError("delta_min must be finite")
    _validate_digest(request.manifest_digest, "manifest_digest")

    pair_count = len(request.full_effect_differences)
    if pair_count < request.minimum_pairs:
        return EligibilityDecision(
            False,
            "insufficient_paired_evidence",
            None,
            pair_count,
            request.manifest_digest,
            request.eligibility_seed_block_id,
        )

    pair_ids, values = _validate_paired_rows(
        request.full_effect_differences,
        request.eligibility_seed_block_id,
        "eligibility",
    )
    if not request.contracts_pass:
        return EligibilityDecision(
            False,
            "full_contract_failed",
            None,
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
            pair_count,
            request.manifest_digest,
            request.eligibility_seed_block_id,
            pair_ids,
        )
    lower_bound = hoeffding_lower_bound(
        values,
        low=request.difference_low,
        high=request.difference_high,
        alpha=request.alpha_F,
    )
    if lower_bound <= request.delta_min:
        return EligibilityDecision(
            False,
            "no_validated_beneficial_effect",
            lower_bound,
            pair_count,
            request.manifest_digest,
            request.eligibility_seed_block_id,
            pair_ids,
        )
    return EligibilityDecision(
        True,
        "eligible",
        lower_bound,
        pair_count,
        request.manifest_digest,
        request.eligibility_seed_block_id,
        pair_ids,
    )


def evaluate_slice_admission(request: SliceAdmissionInput) -> SliceAdmissionDecision:
    if not request.eligibility.admitted:
        return _admission_decision(request, False, request.eligibility.reason)

    candidate = request.candidate
    atom_ids = set(candidate.atom_ids)
    full_atom_ids = set(candidate.full_atom_ids)
    if not atom_ids:
        return _admission_decision(request, False, "empty_slice")
    if len(atom_ids) != len(candidate.atom_ids) or len(full_atom_ids) != len(
        candidate.full_atom_ids
    ):
        return _admission_decision(request, False, "duplicate_atom_id")
    if candidate.atom_ids != tuple(sorted(atom_ids)):
        raise ValueError("candidate atom_ids must use canonical order")
    if candidate.full_atom_ids != tuple(sorted(full_atom_ids)):
        raise ValueError("candidate full_atom_ids must use canonical order")
    if candidate.retained_scc_count != len(atom_ids):
        raise ValueError("retained_scc_count must equal retained atom count")
    if not math.isfinite(candidate.discovery_margin):
        raise ValueError("discovery_margin must be finite")
    if not math.isfinite(candidate.normalized_cost) or not 0.0 <= candidate.normalized_cost <= 1.0:
        raise ValueError("normalized_cost must be finite and within [0, 1]")
    if not atom_ids.issubset(full_atom_ids):
        return _admission_decision(request, False, "unknown_atom")
    if atom_ids == full_atom_ids:
        return _admission_decision(request, False, "not_strict_subset")
    if not candidate.source_valid:
        return _admission_decision(request, False, "invalid_source_atoms")
    if not candidate.executable:
        return _admission_decision(request, False, "non_executable_slice")
    if not candidate.dependency_closed:
        return _admission_decision(request, False, "dependency_not_closed")
    if not request.contracts_pass:
        return _admission_decision(request, False, "slice_contract_failed")
    if not request.guardrails_pass:
        return _admission_decision(request, False, "slice_guardrail_failed")

    for value, label, allow_zero in (
        (request.discovery_queries, "discovery_queries", True),
        (request.query_budget, "query_budget", False),
        (request.minimum_confirmation_pairs, "minimum_confirmation_pairs", False),
    ):
        if isinstance(value, bool) or not isinstance(value, int):
            raise ValueError(f"{label} must be an integer")
        if value < (0 if allow_zero else 1):
            qualifier = "nonnegative" if allow_zero else "positive"
            raise ValueError(f"{label} must be {qualifier}")

    if request.discovery_queries + len(atom_ids) > request.query_budget:
        return _admission_decision(request, False, "insufficient_query_budget")
    if not math.isfinite(request.epsilon) or request.epsilon <= 0:
        raise ValueError("epsilon must be finite and positive")

    _validate_digest(request.manifest_digest, "manifest_digest")
    _validate_digest(request.artifact_digest, "artifact_digest")
    _validate_digest(request.confirmation_registry_digest, "confirmation_registry_digest")
    if request.eligibility.manifest_digest != request.manifest_digest:
        return _admission_decision(request, False, "manifest_digest_mismatch")

    discovery_blocks = request.discovery_seed_block_ids
    if not discovery_blocks or any(not block for block in discovery_blocks):
        raise ValueError("discovery seed blocks must be nonempty")
    if discovery_blocks != tuple(sorted(discovery_blocks)) or len(set(discovery_blocks)) != len(
        discovery_blocks
    ):
        raise ValueError("discovery seed blocks must be unique and canonical")
    forbidden_blocks = set(discovery_blocks)
    if request.eligibility.eligibility_seed_block_id:
        forbidden_blocks.add(request.eligibility.eligibility_seed_block_id)
    if request.confirmation_seed_block_id in forbidden_blocks:
        raise ValueError("confirmation seed block must be disjoint from eligibility and discovery")

    if len(request.gap_differences) < request.minimum_confirmation_pairs:
        return _admission_decision(request, False, "insufficient_confirmation_pairs")
    pair_ids, gap_values = _validate_paired_rows(
        request.gap_differences,
        request.confirmation_seed_block_id,
        "confirmation",
    )
    pair_overlap = set(pair_ids) & set(request.eligibility.pair_ids)
    if pair_overlap:
        raise ValueError(f"confirmation pair IDs overlap eligibility: {sorted(pair_overlap)}")

    origin_map = request.neighbor_origin_map
    if origin_map != tuple(sorted(origin_map)):
        raise ValueError("neighbor_origin_map must use canonical order")
    origins = tuple(origin for origin, _ in origin_map)
    if len(set(origins)) != len(origins):
        raise ValueError("neighbor origins must be unique")
    if any(not origin or not hypothesis for origin, hypothesis in origin_map):
        raise ValueError("neighbor origin mappings must be nonempty")
    missing_origins = sorted(atom_ids - set(origins))
    unexpected_origins = sorted(set(origins) - atom_ids)
    if missing_origins or unexpected_origins:
        failed = missing_origins[0] if missing_origins else unexpected_origins[0]
        return _admission_decision(
            request,
            False,
            "incomplete_neighbor_family",
            failed_hypothesis=failed,
            pair_ids=pair_ids,
        )

    neighbor_p_values = _tuple_map(
        request.neighbor_failure_p_values, "neighbor_failure_p_values"
    )
    registered_neighbors = {hypothesis for _, hypothesis in origin_map}
    actual_neighbors = set(neighbor_p_values)
    if registered_neighbors != actual_neighbors:
        missing = sorted(registered_neighbors - actual_neighbors)
        unexpected = sorted(actual_neighbors - registered_neighbors)
        failed = missing[0] if missing else unexpected[0]
        return _admission_decision(
            request,
            False,
            "incomplete_neighbor_family",
            failed_hypothesis=failed,
            pair_ids=pair_ids,
        )

    sealed_p_values = _tuple_map(request.sealed_p_values, "sealed_p_values")
    duplicated_hypotheses = set(sealed_p_values) & set(neighbor_p_values)
    if duplicated_hypotheses:
        raise ValueError(f"duplicate hypothesis names: {sorted(duplicated_hypotheses)}")
    submitted_family = sealed_p_values | neighbor_p_values

    for hypothesis in REQUIRED_EQUIVALENCE_HYPOTHESES:
        if hypothesis not in submitted_family:
            return _admission_decision(
                request,
                False,
                "incomplete_confirmation_family",
                failed_hypothesis=hypothesis,
                pair_ids=pair_ids,
            )

    expected = request.expected_confirmation_hypothesis_ids
    if not expected or expected != tuple(sorted(expected)) or len(set(expected)) != len(expected):
        raise ValueError("expected confirmation hypotheses must be nonempty, unique, and canonical")
    actual = set(submitted_family)
    expected_set = set(expected)
    if actual != expected_set:
        missing = sorted(expected_set - actual)
        unexpected = sorted(actual - expected_set)
        failed = missing[0] if missing else unexpected[0]
        return _admission_decision(
            request,
            False,
            "confirmation_registry_mismatch",
            failed_hypothesis=failed,
            pair_ids=pair_ids,
        )
    if request.confirmation_registry_digest != _registry_digest(expected):
        return _admission_decision(
            request,
            False,
            "confirmation_registry_digest_mismatch",
            pair_ids=pair_ids,
        )

    gap_interval = hoeffding_interval(
        gap_values,
        low=request.gap_low,
        high=request.gap_high,
        alpha=request.alpha_C,
    )
    if gap_interval[0] < -request.epsilon or gap_interval[1] > request.epsilon:
        return _admission_decision(
            request,
            False,
            "effect_not_equivalent",
            gap_interval=gap_interval,
            pair_ids=pair_ids,
        )

    holm = holm_all_rejected(submitted_family, alpha=request.alpha_C)
    if not holm.all_rejected:
        return _admission_decision(
            request,
            False,
            "confirmation_family_failed",
            gap_interval=gap_interval,
            failed_hypothesis=holm.failed_hypothesis,
            pair_ids=pair_ids,
        )
    return _admission_decision(
        request,
        True,
        "admitted",
        gap_interval=gap_interval,
        pair_ids=pair_ids,
    )
