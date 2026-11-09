from __future__ import annotations

import math

from app.engine.stats import norm_cdf, norm_pdf


def expected_oversell(q: float, mean: float, variance: float) -> float:
    """E[(Q - D)+] for D ~ Normal(mean, variance)."""
    if variance <= 1e-12:
        return max(0.0, q - mean)
    sigma = math.sqrt(variance)
    z = (q - mean) / sigma
    return sigma * (z * norm_cdf(z) + norm_pdf(z))


def expected_sales(q: float, mean: float, variance: float) -> float:
    """E[min(Q, D)] = mean - E[(D - Q)+] = Q - E[(Q - D)+]."""
    return q - expected_oversell(q, mean, variance)


def expected_profit_cup(
    q: float,
    mean: float,
    revenue: float,
    cost: float,
    *,
    variance: float | None = None,
) -> float:
    """
    Classic newsvendor expected profit with Normal demand approximation.

    E[profit] = revenue * E[sales] - cost * Q
              = (revenue - cost) * mean
                - revenue * sigma * (phi(z) - z*(1-Phi(z)))
                - cost * (Q - mean)   [equivalent rearrangement]

    Direct form: revenue * E[min(Q,D)] - cost * Q
    """
    if mean < 0:
        raise ValueError("mean demand must be non-negative")
    if q < 0:
        return float("-inf")
    var = mean if variance is None else max(variance, 0.0)
    sales = expected_sales(q, mean, var)
    return revenue * sales - cost * q


def expected_total_profit(
    hot_q: float,
    cold_q: float,
    hot_mean: float,
    cold_mean: float,
    hot_revenue: float,
    cold_revenue: float,
    hot_cost: float,
    cold_cost: float,
    *,
    barista_cost: float = 0.0,
) -> float:
    hot = expected_profit_cup(hot_q, hot_mean, hot_revenue, hot_cost)
    cold = expected_profit_cup(cold_q, cold_mean, cold_revenue, cold_cost)
    return hot + cold - barista_cost
