from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PairedDifference:
    pair_id: str
    seed_block_id: str
    value: float


@dataclass(frozen=True)
class EligibilityInput:
    full_effect_differences: tuple[PairedDifference, ...]
    eligibility_seed_block_id: str
    difference_low: float
    difference_high: float
    alpha_F: float
    delta_min: float
    minimum_pairs: int
    contracts_pass: bool
    guardrails_pass: bool
    manifest_digest: str


@dataclass(frozen=True)
class EligibilityDecision:
    admitted: bool
    reason: str
    lower_bound: float | None
    pair_count: int
    manifest_digest: str | None = None
    eligibility_seed_block_id: str | None = None
    pair_ids: tuple[str, ...] = ()


@dataclass(frozen=True)
class SliceCandidate:
    atom_ids: tuple[str, ...]
    full_atom_ids: tuple[str, ...]
    retained_scc_count: int
    discovery_margin: float
    normalized_cost: float
    source_valid: bool
    executable: bool
    dependency_closed: bool


@dataclass(frozen=True)
class SliceAdmissionInput:
    eligibility: EligibilityDecision
    candidate: SliceCandidate
    gap_differences: tuple[PairedDifference, ...]
    confirmation_seed_block_id: str
    discovery_seed_block_ids: tuple[str, ...]
    minimum_confirmation_pairs: int
    gap_low: float
    gap_high: float
    epsilon: float
    alpha_C: float
    discovery_queries: int
    query_budget: int
    neighbor_origin_map: tuple[tuple[str, str], ...]
    neighbor_failure_p_values: tuple[tuple[str, float], ...]
    expected_confirmation_hypothesis_ids: tuple[str, ...]
    sealed_p_values: tuple[tuple[str, float], ...]
    confirmation_registry_digest: str
    manifest_digest: str
    artifact_digest: str
    contracts_pass: bool
    guardrails_pass: bool


@dataclass(frozen=True)
class SliceAdmissionDecision:
    admitted: bool
    reason: str
    gap_interval: tuple[float, float] | None = None
    failed_hypothesis: str | None = None
    confirmation_registry_digest: str | None = None
    manifest_digest: str | None = None
    artifact_digest: str | None = None
    confirmation_pair_ids: tuple[str, ...] = ()
