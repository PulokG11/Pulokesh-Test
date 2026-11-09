from __future__ import annotations

from typing import Literal

import numpy as np

from app.engine.expected import expected_profit_for_decisions
from app.models.contracts import CurvePoint, Decisions
from app.scenarios.rounds import RoundScenario

Axis = Literal["hot_brew", "cold_brew", "markup", "service_rate"]


def _clip_decision(scenario: RoundScenario, decisions: Decisions) -> Decisions:
    data = decisions.model_dump()
    for name, bounds in scenario.bounds.items():
        data[name] = float(np.clip(data[name], bounds["min"], bounds["max"]))
    if "hot_brew" not in scenario.active_decisions:
        data["hot_brew"] = 0.0
    if "cold_brew" not in scenario.active_decisions:
        data["cold_brew"] = 0.0
    if not scenario.enable_markup:
        data["markup"] = 0.0
    if not scenario.enable_service_decision:
        data["service_rate"] = scenario.default_service_rate
    return Decisions(**data)


def _profit(scenario: RoundScenario, payload: dict[str, float]) -> float:
    decisions = _clip_decision(scenario, Decisions(**payload))
    value = expected_profit_for_decisions(scenario, decisions)
    return float(value) if np.isfinite(value) else float("-inf")


def optimize_round(scenario: RoundScenario) -> tuple[Decisions, float]:
    """Multi-start coordinate search (SciPy-free for Python 3.15 environments)."""
    names = scenario.active_decisions
    best_payload = scenario.defaults.model_dump()
    best_profit = _profit(scenario, best_payload)

    # Coarse grid over primary axes, then local polish.
    grids: dict[str, np.ndarray] = {}
    for name in names:
        lo = scenario.bounds[name]["min"]
        hi = scenario.bounds[name]["max"]
        grids[name] = np.linspace(lo, hi, 9)

    # Evaluate a manageable cartesian sample by nested loops with pruning for 4D.
    if len(names) == 1:
        candidates = [{names[0]: float(v)} for v in grids[names[0]]]
    elif len(names) == 2:
        a, b = names
        candidates = [{a: float(x), b: float(y)} for x in grids[a] for y in grids[b]]
    else:
        # Sample product partially: fix later vars to defaults while sweeping early ones,
        # then polish all coordinates.
        candidates = []
        base = scenario.defaults.model_dump()
        for name in names:
            for value in grids[name]:
                payload = dict(base)
                payload[name] = float(value)
                candidates.append(payload)
        # A few random joint samples
        rng = np.random.default_rng(42)
        for _ in range(40):
            payload = dict(base)
            for name in names:
                lo = scenario.bounds[name]["min"]
                hi = scenario.bounds[name]["max"]
                payload[name] = float(rng.uniform(lo, hi))
            candidates.append(payload)

    for partial in candidates:
        payload = scenario.defaults.model_dump()
        payload.update(partial)
        profit = _profit(scenario, payload)
        if profit > best_profit:
            best_profit = profit
            best_payload = payload

    # Coordinate descent polish
    for _ in range(8):
        improved = False
        for name in names:
            lo = scenario.bounds[name]["min"]
            hi = scenario.bounds[name]["max"]
            current = best_payload[name]
            span = max(1e-6, (hi - lo) * 0.15)
            for trial in np.linspace(max(lo, current - span), min(hi, current + span), 11):
                payload = dict(best_payload)
                payload[name] = float(trial)
                profit = _profit(scenario, payload)
                if profit > best_profit + 1e-9:
                    best_profit = profit
                    best_payload = payload
                    improved = True
        if not improved:
            break

    best = _clip_decision(scenario, Decisions(**best_payload))
    return best, float(_profit(scenario, best.model_dump()))


def primary_axis(scenario: RoundScenario) -> Axis:
    if scenario.round_number == 8 and "service_rate" in scenario.active_decisions:
        return "service_rate"
    if scenario.round_number == 5 and "markup" in scenario.active_decisions:
        return "markup"
    if "hot_brew" in scenario.active_decisions:
        return "hot_brew"
    if "cold_brew" in scenario.active_decisions:
        return "cold_brew"
    return "markup"


def profit_curve(
    scenario: RoundScenario,
    base: Decisions,
    *,
    axis: Axis | None = None,
    points: int = 41,
) -> tuple[Axis, list[CurvePoint]]:
    axis = axis or primary_axis(scenario)
    lo = scenario.bounds[axis]["min"]
    hi = scenario.bounds[axis]["max"]
    xs = np.linspace(lo, hi, points)
    curve: list[CurvePoint] = []
    for x in xs:
        payload = base.model_dump()
        payload[axis] = float(x)
        profit = _profit(scenario, payload)
        if not np.isfinite(profit):
            continue
        curve.append(CurvePoint(x=float(x), expected_profit=float(profit)))
    return axis, curve
