from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Mapping, Sequence


@dataclass(frozen=True)
class HolmResult:
    all_rejected: bool
    failed_hypothesis: str | None
    failed_p_value: float | None
    failed_threshold: float | None


def _validate_samples(values: Sequence[float], low: float, high: float, alpha: float) -> list[float]:
    if not 0.0 < alpha < 1.0:
        raise ValueError("alpha must be strictly between 0 and 1")
    if not math.isfinite(low) or not math.isfinite(high) or low >= high:
        raise ValueError("declared bounds must be finite and low < high")
    samples = [float(value) for value in values]
    if not samples:
        raise ValueError("at least one sample is required")
    if any(not math.isfinite(value) for value in samples):
        raise ValueError("samples must be finite")
    if any(value < low or value > high for value in samples):
        raise ValueError("sample is outside declared bounds")
    return samples


def hoeffding_lower_bound(values: Sequence[float], low: float, high: float, alpha: float) -> float:
    samples = _validate_samples(values, low, high, alpha)
    radius = (high - low) * math.sqrt(math.log(1.0 / alpha) / (2.0 * len(samples)))
    return sum(samples) / len(samples) - radius


def hoeffding_interval(
    values: Sequence[float], low: float, high: float, alpha: float
) -> tuple[float, float]:
    samples = _validate_samples(values, low, high, alpha)
    mean = sum(samples) / len(samples)
    radius = (high - low) * math.sqrt(math.log(2.0 / alpha) / (2.0 * len(samples)))
    return mean - radius, mean + radius


def holm_all_rejected(p_values: Mapping[str, float], alpha: float) -> HolmResult:
    if not 0.0 < alpha < 1.0:
        raise ValueError("alpha must be strictly between 0 and 1")
    if not p_values:
        raise ValueError("at least one hypothesis is required")
    ordered: list[tuple[str, float]] = []
    for name, raw_p_value in p_values.items():
        p_value = float(raw_p_value)
        if not math.isfinite(p_value) or not 0.0 <= p_value <= 1.0:
            raise ValueError(f"invalid p-value for {name}")
        ordered.append((name, p_value))
    ordered.sort(key=lambda item: (item[1], item[0]))
    total = len(ordered)
    for index, (name, p_value) in enumerate(ordered):
        threshold = alpha / (total - index)
        if p_value > threshold:
            return HolmResult(False, name, p_value, threshold)
    return HolmResult(True, None, None, None)
