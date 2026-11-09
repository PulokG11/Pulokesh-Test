from __future__ import annotations

from app.models.contracts import Decisions, FeasibilityResult
from app.scenarios.rounds import RoundScenario


def check_feasibility(scenario: RoundScenario, decisions: Decisions) -> FeasibilityResult:
    hot = decisions.hot_brew if "hot_brew" in scenario.active_decisions else 0.0
    cold = decisions.cold_brew if "cold_brew" in scenario.active_decisions else 0.0

    beans_used = hot * scenario.beans_per_hot + cold * scenario.beans_per_cold
    water_used = hot * scenario.water_per_hot + cold * scenario.water_per_cold

    messages: list[str] = []
    if beans_used > scenario.beans_cap + 1e-9:
        messages.append(
            f"Beans needed ({beans_used:.1f}) exceed capacity ({scenario.beans_cap:.1f})."
        )
    if water_used > scenario.water_cap + 1e-9:
        messages.append(
            f"Water needed ({water_used:.1f}) exceed capacity ({scenario.water_cap:.1f})."
        )

    return FeasibilityResult(
        feasible=len(messages) == 0,
        beans_used=beans_used,
        water_used=water_used,
        beans_cap=scenario.beans_cap,
        water_cap=scenario.water_cap,
        messages=messages,
    )
