from __future__ import annotations

from app.engine.feasibility import check_feasibility
from app.engine.newsvendor import expected_total_profit
from app.engine.queueing import barista_hourly_cost, effective_means
from app.models.contracts import Decisions
from app.scenarios.rounds import RoundScenario


def revenues(scenario: RoundScenario, markup: float) -> tuple[float, float]:
    m = markup if scenario.enable_markup else 0.0
    return scenario.base_price_hot + m, scenario.base_price_cold + m


def expected_profit_for_decisions(scenario: RoundScenario, decisions: Decisions) -> float:
    feasibility = check_feasibility(scenario, decisions)
    if not feasibility.feasible:
        return float("-inf")

    markup = decisions.markup if scenario.enable_markup else 0.0
    _, hot_mean, cold_mean = effective_means(
        scenario.base_lambda,
        scenario.hot_prob,
        markup,
        scenario.markup_sensitivity,
        scenario.cups_per_customer,
        enable_markup=scenario.enable_markup,
        enable_multi_cup=scenario.enable_multi_cup,
    )

    # Balking reduces effective served demand in expectation via utilization proxy.
    service_rate = (
        decisions.service_rate
        if scenario.enable_service_decision
        else scenario.default_service_rate
    )
    if scenario.enable_balking:
        # Approximate fraction retained when arrival rate approaches service capacity.
        retention = min(1.0, service_rate / max(scenario.base_lambda, 1e-6))
        # Soften with balk scale: longer implied queues hurt more.
        retention *= scenario.balk_scale / (scenario.balk_scale + max(0.0, scenario.base_lambda - service_rate))
        retention = max(0.35, min(1.0, retention))
        hot_mean *= retention
        cold_mean *= retention

    hot_q = decisions.hot_brew if "hot_brew" in scenario.active_decisions else 0.0
    cold_q = decisions.cold_brew if "cold_brew" in scenario.active_decisions else 0.0
    hot_rev, cold_rev = revenues(scenario, markup)

    barista_cost = 0.0
    if scenario.enable_service_decision:
        barista_cost = barista_hourly_cost(
            service_rate, scenario.barista_base_cost, scenario.barista_cost_slope
        )

    return expected_total_profit(
        hot_q,
        cold_q,
        hot_mean,
        cold_mean if "cold_brew" in scenario.active_decisions else 0.0,
        hot_rev,
        cold_rev,
        scenario.hot_cost if "hot_brew" in scenario.active_decisions else 0.0,
        scenario.cold_cost if "cold_brew" in scenario.active_decisions else 0.0,
        barista_cost=barista_cost,
    )
