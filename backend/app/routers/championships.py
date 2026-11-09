from __future__ import annotations

import csv
import io

from fastapi import APIRouter, Header, HTTPException, Response

from app.config import get_settings
from app.db import repository
from app.models.contracts import (
    ChampionshipCreateRequest,
    ChampionshipCreateResponse,
    ChampionshipJoinRequest,
    ChampionshipJoinResponse,
    LeaderboardResponse,
)

router = APIRouter(prefix="/championships", tags=["championships"])


def _require_instructor(x_instructor_key: str | None) -> None:
    settings = get_settings()
    if not x_instructor_key or x_instructor_key != settings.instructor_api_key:
        raise HTTPException(status_code=401, detail="Invalid instructor API key")


@router.post("", response_model=ChampionshipCreateResponse)
def create_championship(
    body: ChampionshipCreateRequest,
    x_instructor_key: str | None = Header(default=None),
) -> ChampionshipCreateResponse:
    _require_instructor(x_instructor_key)
    try:
        record = repository.create_championship(
            body.match_code.strip(), body.title.strip(), body.scenario_set_id.strip()
        )
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except Exception as exc:  # unique violation etc.
        raise HTTPException(status_code=409, detail=f"Could not create championship: {exc}") from exc
    return ChampionshipCreateResponse(
        id=record["id"],
        match_code=record["match_code"],
        title=record["title"],
        scenario_set_id=record["scenario_set_id"],
    )


@router.post("/join", response_model=ChampionshipJoinResponse)
def join_championship(body: ChampionshipJoinRequest) -> ChampionshipJoinResponse:
    try:
        record = repository.join_championship(body.match_code.strip(), body.display_name.strip())
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return ChampionshipJoinResponse(**record)


@router.get("/{match_code}/leaderboard", response_model=LeaderboardResponse)
def get_leaderboard(match_code: str) -> LeaderboardResponse:
    try:
        entries = repository.leaderboard(match_code)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return LeaderboardResponse(match_code=match_code, entries=entries)


@router.get("/{match_code}/export")
def export_leaderboard(
    match_code: str,
    x_instructor_key: str | None = Header(default=None),
) -> Response:
    _require_instructor(x_instructor_key)
    try:
        entries = repository.leaderboard(match_code)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(["display_name", "total_realized_profit", "rounds_completed", "last_submitted_at"])
    for entry in entries:
        writer.writerow(
            [
                entry.display_name,
                f"{entry.total_realized_profit:.4f}",
                entry.rounds_completed,
                entry.last_submitted_at or "",
            ]
        )
    return Response(
        content=buffer.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{match_code}-leaderboard.csv"'},
    )


@router.post("/play-session")
def create_play_session(display_name: str = "Player") -> dict:
    session_id = repository.create_play_session(display_name)
    return {"session_id": session_id, "display_name": display_name, "mode": "play"}
