from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PairedDifference:
    pair_id: str
    seed_block_id: str
    value: float


@dataclass(frozen=True)
class BinaryObservation:
    pair_id: str
    seed_block_id: str
    violated: bool


@dataclass(frozen=True)
class ConfirmationHypothesisSpec:
    hypothesis_id: str
    maximum_violation_rate: float


@dataclass(frozen=True)
class ViolationHypothesisEvidence:
    hypothesis_id: str
    maximum_violation_rate: float
    observations: tuple[BinaryObservation, ...]


@dataclass(frozen=True)
class EligibilityInput:
    full_effect_differences: tuple[PairedDifference, ...]
    eligibility_seed_block_id: str
    alpha_F: float
    delta_min: float
    minimum_beneficial_prevalence: float
    minimum_pairs: int
    contracts_pass: bool
    guardrails_pass: bool
    manifest_digest: str


@dataclass(frozen=True)
class EligibilityDecision:
    admitted: bool
    reason: str
    beneficial_prevalence_lower_bound: float | None
    beneficial_count: int
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
    source_valid: bool
    executable: bool
    dependency_closed: bool


@dataclass(frozen=True)
class HypothesisResult:
    hypothesis_id: str
    maximum_violation_rate: float
    violation_count: int
    pair_count: int
    p_value: float
    holm_threshold: float
    simultaneous_upper_bound: float
    rejected: bool


@dataclass(frozen=True)
class SealedConfirmationInput:
    eligibility: EligibilityDecision
    candidate: SliceCandidate
    confirmation_seed_block_id: str
    discovery_seed_block_ids: tuple[str, ...]
    minimum_confirmation_pairs: int
    alpha_C: float
    discovery_queries: int
    query_budget: int
    neighbor_origin_map: tuple[tuple[str, str], ...]
    expected_confirmation_specs: tuple[ConfirmationHypothesisSpec, ...]
    expected_confirmation_pair_ids: tuple[str, ...]
    confirmation_evidence: tuple[ViolationHypothesisEvidence, ...]
    confirmation_registry_digest: str
    manifest_digest: str
    artifact_digest: str
    contracts_pass: bool
    guardrails_pass: bool
    cost_constraints_pass: bool


@dataclass(frozen=True)
class SealedConfirmationDecision:
    admitted: bool
    reason: str
    failed_hypothesis: str | None = None
    hypothesis_results: tuple[HypothesisResult, ...] = ()
    confirmation_registry_digest: str | None = None
    manifest_digest: str | None = None
    artifact_digest: str | None = None
    confirmation_pair_ids: tuple[str, ...] = ()

