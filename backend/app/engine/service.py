from __future__ import annotations

from app.config import get_settings
from app.engine.des import simulate_shop
from app.engine.expected import expected_profit_for_decisions
from app.engine.feasibility import check_feasibility
from app.engine.optimizer import optimize_round, profit_curve
from app.models.contracts import ComparisonResponse, Decisions, SimulateResponse
from app.scenarios.rounds import get_round


def evaluate_decisions(
    round_number: int,
    decisions: Decisions,
    *,
    seed: int | None = None,
    hours: int | None = None,
) -> SimulateResponse:
    scenario = get_round(round_number)
    settings = get_settings()
    sim_hours = hours or settings.score_hours
    feasibility = check_feasibility(scenario, decisions)
    # Model expected profit is per hour; scale to the scoring horizon.
    expected_hourly = expected_profit_for_decisions(scenario, decisions)
    expected = expected_hourly * sim_hours if feasibility.feasible else float("-inf")
    sim = simulate_shop(scenario, decisions, hours=sim_hours, seed=seed)
    return SimulateResponse(
        feasible=feasibility,
        realized_profit=sim.realized_profit if feasibility.feasible else float("-inf"),
        expected_profit=expected,
        metrics=sim.metrics,
        seed=sim.seed,
    )


def submit_round(
    round_number: int,
    decisions: Decisions,
    *,
    seed: int | None = None,
) -> ComparisonResponse:
    scenario = get_round(round_number)
    settings = get_settings()
    hours = settings.score_hours
    feasibility = check_feasibility(scenario, decisions)
    player_expected = expected_profit_for_decisions(scenario, decisions) * hours
    player_sim = simulate_shop(scenario, decisions, hours=hours, seed=seed)

    optimal, optimal_expected_hourly = optimize_round(scenario)
    optimal_expected = optimal_expected_hourly * hours
    # Same seed: realized gap is decision noise, not a different random draw.
    optimal_sim = simulate_shop(
        scenario, optimal, hours=hours, seed=player_sim.seed
    )
    axis, curve = profit_curve(scenario, optimal)
    scaled_curve = [
        point.model_copy(update={"expected_profit": point.expected_profit * hours})
        for point in curve
    ]

    return ComparisonResponse(
        player_decisions=decisions,
        optimal_decisions=optimal,
        player_expected_profit=player_expected if feasibility.feasible else float("-inf"),
        optimal_expected_profit=optimal_expected,
        player_realized_profit=player_sim.realized_profit if feasibility.feasible else float("-inf"),
        optimal_realized_profit=optimal_sim.realized_profit,
        curve_axis=axis,
        curve=scaled_curve,
        metrics=player_sim.metrics,
        seed=player_sim.seed,
        feasible=feasibility,
    )
