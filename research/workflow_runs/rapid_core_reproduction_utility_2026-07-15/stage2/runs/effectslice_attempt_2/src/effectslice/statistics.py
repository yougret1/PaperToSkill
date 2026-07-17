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


def _validate_count(violations: int, total: int) -> None:
    if isinstance(violations, bool) or not isinstance(violations, int):
        raise ValueError("violations must be an integer")
    if isinstance(total, bool) or not isinstance(total, int):
        raise ValueError("total must be an integer")
    if total < 1:
        raise ValueError("total must be positive")
    if not 0 <= violations <= total:
        raise ValueError("violations must be between zero and total")


def _validate_probability(value: float, label: str) -> float:
    probability = float(value)
    if not math.isfinite(probability) or not 0.0 < probability < 1.0:
        raise ValueError(f"{label} must be strictly between 0 and 1")
    return probability


def exact_binomial_lower_tail_p_value(
    violations: int,
    total: int,
    maximum_violation_rate: float,
) -> float:
    """Return P[X <= violations] for X~Binomial(total, rate boundary)."""
    _validate_count(violations, total)
    rate = _validate_probability(maximum_violation_rate, "maximum_violation_rate")
    log_rate = math.log(rate)
    log_complement = math.log1p(-rate)
    terms = []
    for count in range(violations + 1):
        log_term = (
            math.lgamma(total + 1)
            - math.lgamma(count + 1)
            - math.lgamma(total - count + 1)
            + count * log_rate
            + (total - count) * log_complement
        )
        terms.append(math.exp(log_term))
    return min(1.0, math.fsum(terms))


def clopper_pearson_upper_bound(
    violations: int,
    total: int,
    alpha: float,
) -> float:
    """Return the one-sided exact upper bound for a binomial violation rate."""
    _validate_count(violations, total)
    tail_alpha = _validate_probability(alpha, "alpha")
    if violations == total:
        return 1.0
    if violations == 0:
        return 1.0 - tail_alpha ** (1.0 / total)

    lower = violations / total
    upper = 1.0
    for _ in range(100):
        midpoint = (lower + upper) / 2.0
        cdf = exact_binomial_lower_tail_p_value(violations, total, midpoint)
        if cdf > tail_alpha:
            lower = midpoint
        else:
            upper = midpoint
    return (lower + upper) / 2.0


def zero_violation_sample_size(
    maximum_violation_rate: float,
    alpha: float,
    family_size: int = 1,
) -> int:
    """Return the minimum n whose zero-violation p-value clears alpha/m."""
    rate = _validate_probability(maximum_violation_rate, "maximum_violation_rate")
    family_alpha = _validate_probability(alpha, "alpha")
    if isinstance(family_size, bool) or not isinstance(family_size, int) or family_size < 1:
        raise ValueError("family_size must be a positive integer")
    threshold = family_alpha / family_size
    sample_size = math.ceil(math.log(threshold) / math.log1p(-rate))
    while (1.0 - rate) ** sample_size > threshold:
        sample_size += 1
    while sample_size > 1 and (1.0 - rate) ** (sample_size - 1) <= threshold:
        sample_size -= 1
    return sample_size


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
