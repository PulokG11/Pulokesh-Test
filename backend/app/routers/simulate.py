from fastapi import APIRouter, HTTPException

from app.engine.optimizer import optimize_round, profit_curve
from app.engine.service import evaluate_decisions, submit_round
from app.models.contracts import (
    OptimizeRequest,
    OptimizeResponse,
    SimulateRequest,
    SimulateResponse,
    SubmitRequest,
    SubmitResponse,
)
from app.db import repository
from app.scenarios.rounds import get_round

router = APIRouter(tags=["simulate"])


@router.post("/simulate", response_model=SimulateResponse)
def simulate(body: SimulateRequest) -> SimulateResponse:
    try:
        get_round(body.round_number)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return evaluate_decisions(
        body.round_number,
        body.decisions,
        seed=body.seed,
        hours=body.hours,
    )


@router.post("/optimize", response_model=OptimizeResponse)
def optimize(body: OptimizeRequest) -> OptimizeResponse:
    try:
        scenario = get_round(body.round_number)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    from app.config import get_settings

    settings = get_settings()
    hours = settings.score_hours
    optimal, expected_hourly = optimize_round(scenario)
    base = body.decisions or optimal
    axis, curve = profit_curve(scenario, base)
    return OptimizeResponse(
        optimal_decisions=optimal,
        expected_profit=expected_hourly * hours,
        curve_axis=axis,
        curve=[
            point.model_copy(update={"expected_profit": point.expected_profit * hours})
            for point in curve
        ],
    )


@router.post("/submit", response_model=SubmitResponse)
def submit(body: SubmitRequest) -> SubmitResponse:
    try:
        get_round(body.round_number)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    comparison = submit_round(body.round_number, body.decisions, seed=body.seed)
    submission_id = None
    if body.session_id:
        try:
            submission_id = repository.save_submission(
                body.session_id,
                body.round_number,
                body.decisions,
                comparison.player_realized_profit,
                comparison.player_expected_profit,
                comparison.optimal_expected_profit,
                comparison.seed,
            )
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
    return SubmitResponse(comparison=comparison, submission_id=submission_id)
