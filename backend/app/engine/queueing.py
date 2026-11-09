from __future__ import annotations

import math


def arrival_rate_from_markup(base_lambda: float, markup: float, sensitivity: float) -> float:
    """Higher markup reduces arrivals. Soft exponential decay."""
    return max(0.05, base_lambda * math.exp(-sensitivity * max(0.0, markup)))


def balking_probability(queue_length: int, balk_scale: float) -> float:
    """Probability an arrival leaves without joining as queue grows."""
    if balk_scale <= 0:
        return 0.0
    return 1.0 - math.exp(-queue_length / balk_scale)


def barista_hourly_cost(service_rate: float, base_cost: float, cost_slope: float) -> float:
    """Wage rises with service capability."""
    return base_cost + cost_slope * max(0.0, service_rate)


def effective_means(
    base_lambda: float,
    hot_prob: float,
    markup: float,
    markup_sensitivity: float,
    cups_per_customer: float,
    *,
    enable_markup: bool,
    enable_multi_cup: bool,
) -> tuple[float, float, float]:
    """Return (lambda_total, hot_mean_cups/hour, cold_mean_cups/hour)."""
    lam = arrival_rate_from_markup(base_lambda, markup, markup_sensitivity) if enable_markup else base_lambda
    cups = cups_per_customer if enable_multi_cup else 1.0
    hot_mean = lam * hot_prob * cups
    cold_mean = lam * (1.0 - hot_prob) * cups
    return lam, hot_mean, cold_mean
