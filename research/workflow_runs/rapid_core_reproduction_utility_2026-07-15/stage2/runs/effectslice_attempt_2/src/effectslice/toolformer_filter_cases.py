from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Any

import numpy as np


BLOCK_SEEDS = {
    "development": tuple(range(31_000, 31_004)),
    "eligibility": tuple(range(32_000, 32_021)),
    "discovery": tuple(range(33_000, 33_016)),
    "confirmation": tuple(range(34_000, 34_059)),
    "confirmation_v2": tuple(range(35_000, 35_064)),
    "confirmation_v4": tuple(range(37_000, 37_064)),
    "confirmation_v5": tuple(range(47_000, 47_064)),
}


def paper_weights(horizon: int) -> np.ndarray:
    if isinstance(horizon, bool) or not isinstance(horizon, (int, np.integer)):
        raise ValueError("horizon must be an integer")
    if int(horizon) < 1:
        raise ValueError("horizon must be positive")
    raw = np.maximum(0.0, 1.0 - 0.2 * np.arange(int(horizon), dtype=np.float64))
    total = float(raw.sum())
    if total <= 0 or not math.isfinite(total):
        raise ValueError("paper weights cannot be normalized")
    return raw / total


def _validated_logp(value: Any, name: str) -> np.ndarray:
    try:
        array = np.asarray(value, dtype=np.float64)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name} must be a numeric matrix") from exc
    if array.ndim != 2 or array.shape[0] < 1 or array.shape[1] < 1:
        raise ValueError(f"{name} must be a nonempty two-dimensional matrix")
    if not np.isfinite(array).all() or np.any(array > 0):
        raise ValueError(f"{name} must contain finite nonpositive log probabilities")
    return array


def paper_filter_api_calls(
    logp_with_result: Any,
    logp_call_only: Any,
    logp_no_call: Any,
    tau_filter: float,
) -> tuple[np.ndarray, np.ndarray]:
    with_result = _validated_logp(logp_with_result, "logp_with_result")
    call_only = _validated_logp(logp_call_only, "logp_call_only")
    no_call = _validated_logp(logp_no_call, "logp_no_call")
    if call_only.shape != with_result.shape or no_call.shape != with_result.shape:
        raise ValueError("all log-probability matrices must have the same shape")
    if isinstance(tau_filter, bool) or not isinstance(
        tau_filter, (int, float, np.integer, np.floating)
    ):
        raise ValueError("tau_filter must be numeric")
    tau = float(tau_filter)
    if not math.isfinite(tau) or tau < 0:
        raise ValueError("tau_filter must be finite and nonnegative")
    weights = paper_weights(with_result.shape[1])
    l_plus = -(with_result * weights).sum(axis=1)
    l_call_only = -(call_only * weights).sum(axis=1)
    l_empty = -(no_call * weights).sum(axis=1)
    margins = np.minimum(l_empty, l_call_only) - l_plus
    return margins >= tau, margins


def _generate_v1_case(seed: int) -> dict[str, Any]:
    if isinstance(seed, bool) or not isinstance(seed, int):
        raise ValueError("seed must be an integer")
    rng = np.random.default_rng(seed)
    horizon = 2 + seed % 7
    tau = (0.0, 0.125, 0.25, 0.5)[seed % 4]
    n_candidates = 4
    no_nll = np.full((n_candidates, horizon), 3.0, dtype=np.float64)
    call_nll = np.full((n_candidates, horizon), 3.2, dtype=np.float64)
    full_nll = np.empty((n_candidates, horizon), dtype=np.float64)

    # Beneficial under paper weights, but rejected by a uniform-weight shortcut.
    weights = paper_weights(horizon)
    uniform_trap = np.zeros(horizon, dtype=np.float64)
    uniform_trap[-1] = -8.0
    uniform_trap[0] = -weights[-1] * uniform_trap[-1] / weights[0]
    no_nll[0] = 10.0 + uniform_trap
    call_nll[0] = 10.0 + uniform_trap
    paper_baseline = float(weights @ no_nll[0])
    full_nll[0] = paper_baseline - (tau + 0.3)

    # Exact inclusive ties use tau=0; other thresholds stay just above the boundary.
    call_nll[1] = 4.0
    tie_margin = tau if tau == 0 else tau + 1e-6
    full_nll[1] = no_nll[1] - tie_margin

    # Below-threshold candidate under either counterfactual.
    desired_margin = tau - 0.1
    full_nll[2] = 3.0 - desired_margin

    # Comparator trap: no-call looks helpful, but call-only is the tighter baseline.
    no_nll[3] = 4.0
    call_nll[3] = 2.0
    full_nll[3] = 2.0 - (tau - 0.05)

    # Add paper-weight-zero tail noise without changing the oracle result.
    if horizon > 5:
        no_nll[:, 5:] += rng.uniform(2.0, 8.0, size=(n_candidates, horizon - 5))
        call_nll[:, 5:] += rng.uniform(1.0, 6.0, size=(n_candidates, horizon - 5))
        full_nll[:, 5:] += rng.uniform(3.0, 9.0, size=(n_candidates, horizon - 5))

    case = {
        "case_id": f"toolformer-filter-{seed}",
        "seed": seed,
        "tau_filter": tau,
        "logp_with_result": (-full_nll).tolist(),
        "logp_call_only": (-call_nll).tolist(),
        "logp_no_call": (-no_nll).tolist(),
    }
    keep, margins = paper_filter_api_calls(
        case["logp_with_result"],
        case["logp_call_only"],
        case["logp_no_call"],
        case["tau_filter"],
    )
    if keep.tolist() != [True, True, False, False]:
        raise ValueError(f"generated case lost its decision contract: {seed}")
    if not np.isfinite(margins).all():
        raise ValueError(f"generated case has nonfinite margins: {seed}")
    return case


def _generate_v2_case(seed: int) -> dict[str, Any]:
    rng = np.random.default_rng(seed)
    horizon = 2 + ((seed // 3) % 9)
    n_candidates = 3 + (seed % 5)
    tau = (0.0, 0.05, 0.125, 0.25, 0.5, 0.75)[seed % 6]
    weights = paper_weights(horizon)
    no_nll = rng.uniform(2.5, 6.5, size=(n_candidates, horizon))
    call_nll = rng.uniform(2.5, 6.5, size=(n_candidates, horizon))
    baseline_losses = np.minimum(no_nll @ weights, call_nll @ weights)

    keep_count = 1 + ((seed // 5) % n_candidates)
    rotation = (seed // 11) % n_candidates
    keep_indices = {
        (rotation + offset) % n_candidates for offset in range(keep_count)
    }
    tie_index = rotation
    full_nll = np.empty_like(no_nll)
    expected_keep = []
    for index in range(n_candidates):
        should_keep = index in keep_indices
        expected_keep.append(should_keep)
        if index == tie_index:
            target_margin = tau + 5e-13
        elif should_keep:
            target_margin = tau + 0.15 + 0.01 * (index % 3)
        else:
            target_margin = tau - 0.05 - 0.02 * (index % 3)
        shape = rng.normal(0.0, 0.04, size=horizon)
        shape -= float(weights @ shape)
        full_nll[index] = baseline_losses[index] - target_margin + shape

    case = {
        "case_id": f"toolformer-filter-v2-{seed}",
        "seed": seed,
        "tau_filter": tau,
        "logp_with_result": (-full_nll).tolist(),
        "logp_call_only": (-call_nll).tolist(),
        "logp_no_call": (-no_nll).tolist(),
    }
    keep, margins = paper_filter_api_calls(
        case["logp_with_result"],
        case["logp_call_only"],
        case["logp_no_call"],
        case["tau_filter"],
    )
    if keep.tolist() != expected_keep:
        raise ValueError(f"v2 case lost its decision contract: {seed}")
    if not np.isfinite(margins).all():
        raise ValueError(f"v2 case has nonfinite margins: {seed}")
    return case


def generate_case(seed: int) -> dict[str, Any]:
    if isinstance(seed, bool) or not isinstance(seed, int):
        raise ValueError("seed must be an integer")
    if seed in (
        *BLOCK_SEEDS["confirmation_v2"],
        *BLOCK_SEEDS["confirmation_v4"],
        *BLOCK_SEEDS["confirmation_v5"],
    ):
        return _generate_v2_case(seed)
    return _generate_v1_case(seed)


def build_case_registry(output_path: Path) -> dict[str, Any]:
    registry = {
        "schema_version": "effectslice-toolformer-filter-case-registry.v1",
        "task_id": "TOOLFORMER-FILTER",
        "blocks": {
            name: [generate_case(seed) for seed in seeds]
            for name, seeds in BLOCK_SEEDS.items()
        },
        "evidence_boundary": (
            "Frozen deterministic private cases; not model-visible and not results."
        ),
    }
    destination = Path(output_path).resolve()
    destination.parent.mkdir(parents=True, exist_ok=True)
    serialized = json.dumps(registry, indent=2, ensure_ascii=False) + "\n"
    destination.write_text(serialized, encoding="utf-8", newline="\n")
    return {
        **registry,
        "registry_sha256": hashlib.sha256(serialized.encode("utf-8")).hexdigest(),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build Toolformer filter cases")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    registry = build_case_registry(args.output)
    print(
        json.dumps(
            {
                "registry_sha256": registry["registry_sha256"],
                "block_counts": {
                    name: len(cases) for name, cases in registry["blocks"].items()
                },
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
