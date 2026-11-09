from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np

from app.engine.feasibility import check_feasibility
from app.engine.queueing import arrival_rate_from_markup, balking_probability, barista_hourly_cost
from app.models.contracts import Decisions
from app.scenarios.rounds import RoundScenario


@dataclass
class SimulationResult:
    realized_profit: float
    metrics: dict[str, float]
    seed: int


def simulate_shop(
    scenario: RoundScenario,
    decisions: Decisions,
    *,
    hours: int = 120,
    seed: int | None = None,
) -> SimulationResult:
    """Discrete-time hourly shop simulation with Poisson arrivals."""
    feasibility = check_feasibility(scenario, decisions)
    if not feasibility.feasible:
        return SimulationResult(
            realized_profit=float("-inf"),
            metrics={"infeasible": 1.0},
            seed=0 if seed is None else seed,
        )

    rng = np.random.default_rng(seed)
    used_seed = int(rng.integers(0, 2**31 - 1)) if seed is None else seed
    rng = np.random.default_rng(used_seed)

    markup = decisions.markup if scenario.enable_markup else 0.0
    lam = (
        arrival_rate_from_markup(scenario.base_lambda, markup, scenario.markup_sensitivity)
        if scenario.enable_markup
        else scenario.base_lambda
    )
    service_rate = (
        decisions.service_rate
        if scenario.enable_service_decision
        else scenario.default_service_rate
    )
    hot_q = decisions.hot_brew if "hot_brew" in scenario.active_decisions else 0.0
    cold_q = decisions.cold_brew if "cold_brew" in scenario.active_decisions else 0.0
    hot_price = scenario.base_price_hot + markup
    cold_price = scenario.base_price_cold + markup
    cups_per = scenario.cups_per_customer if scenario.enable_multi_cup else 1.0

    queue = 0
    profit = 0.0
    customers_arrived = 0
    customers_served = 0
    customers_balked = 0
    customers_stockout = 0
    hot_sold = 0.0
    cold_sold = 0.0
    hot_waste = 0.0
    cold_waste = 0.0
    queue_length_sum = 0.0

    barista_cost_per_hour = (
        barista_hourly_cost(service_rate, scenario.barista_base_cost, scenario.barista_cost_slope)
        if scenario.enable_service_decision
        else 0.0
    )

    for _ in range(hours):
        # Fresh brew for the hour.
        hot_inv = hot_q
        cold_inv = cold_q

        arrivals = int(rng.poisson(lam))
        customers_arrived += arrivals

        for _arrival in range(arrivals):
            if scenario.enable_balking:
                p_balk = balking_probability(queue, scenario.balk_scale)
                if rng.random() < p_balk:
                    customers_balked += 1
                    continue
            queue += 1

        # Serve up to service_rate customers this hour (exponential-ish via Poisson capacity).
        capacity = max(0, int(rng.poisson(service_rate)))
        served = min(queue, capacity)
        queue -= served

        for _ in range(served):
            wants_hot = rng.random() < scenario.hot_prob
            order_cups = cups_per if (not scenario.enable_multi_cup or rng.random() < 0.7) else 1.0
            if scenario.enable_multi_cup:
                # Mix of 1 and multi-cup orders with mean near cups_per.
                order_cups = 1.0 if rng.random() < 0.4 else max(1.0, float(rng.integers(2, 4)))
                # Re-center toward configured mean.
                order_cups = 1.0 + (order_cups - 1.0) * (cups_per - 1.0) / 1.5

            if wants_hot or "cold_brew" not in scenario.active_decisions:
                take = min(hot_inv, order_cups)
                if take <= 1e-9:
                    customers_stockout += 1
                    continue
                hot_inv -= take
                hot_sold += take
                profit += hot_price * take
                customers_served += 1
            else:
                take = min(cold_inv, order_cups)
                if take <= 1e-9:
                    customers_stockout += 1
                    continue
                cold_inv -= take
                cold_sold += take
                profit += cold_price * take
                customers_served += 1

        # Charge brewing cost on the full committed brew quantity (sold + waste).
        profit -= scenario.hot_cost * hot_q
        if "cold_brew" in scenario.active_decisions:
            profit -= scenario.cold_cost * cold_q

        hot_waste += hot_inv
        cold_waste += cold_inv
        profit -= barista_cost_per_hour
        queue_length_sum += queue

    metrics = {
        "customers_arrived": float(customers_arrived),
        "customers_served": float(customers_served),
        "customers_balked": float(customers_balked),
        "customers_stockout": float(customers_stockout),
        "hot_sold": float(hot_sold),
        "cold_sold": float(cold_sold),
        "hot_waste": float(hot_waste),
        "cold_waste": float(cold_waste),
        "avg_queue": float(queue_length_sum / max(hours, 1)),
        "hours": float(hours),
        "arrival_rate": float(lam),
        "service_rate": float(service_rate),
    }

    if not math.isfinite(profit):
        profit = float("-inf")

    return SimulationResult(realized_profit=float(profit), metrics=metrics, seed=used_seed)
