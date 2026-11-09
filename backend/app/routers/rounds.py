from fastapi import APIRouter, HTTPException

from app.models.contracts import RoundInfo, RoundListResponse
from app.scenarios.rounds import get_round, list_rounds

router = APIRouter(prefix="/rounds", tags=["rounds"])


@router.get("", response_model=RoundListResponse)
def get_rounds() -> RoundListResponse:
    return RoundListResponse(rounds=list_rounds())


@router.get("/{round_number}", response_model=RoundInfo)
def get_round_info(round_number: int) -> RoundInfo:
    try:
        scenario = get_round(round_number)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return next(r for r in list_rounds() if r.round_number == scenario.round_number)
