from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


class Decisions(BaseModel):
    hot_brew: float = Field(0.0, ge=0)
    cold_brew: float = Field(0.0, ge=0)
    markup: float = Field(0.0, ge=0)
    service_rate: float = Field(20.0, ge=0.1)


class FeasibilityResult(BaseModel):
    feasible: bool
    beans_used: float
    water_used: float
    beans_cap: float
    water_cap: float
    messages: list[str] = Field(default_factory=list)


class RoundInfo(BaseModel):
    round_number: int
    title: str
    description: str
    tip: str
    active_decisions: list[str]
    defaults: Decisions
    bounds: dict[str, dict[str, float]]
    scenario: dict[str, Any]
    features: dict[str, bool]


class RoundListResponse(BaseModel):
    rounds: list[RoundInfo]


class SimulateRequest(BaseModel):
    round_number: int = Field(..., ge=1, le=8)
    decisions: Decisions
    seed: int | None = None
    hours: int | None = Field(None, ge=1, le=240)


class SimulateResponse(BaseModel):
    feasible: FeasibilityResult
    realized_profit: float
    expected_profit: float
    metrics: dict[str, float]
    seed: int


class CurvePoint(BaseModel):
    x: float
    expected_profit: float


class OptimizeRequest(BaseModel):
    round_number: int = Field(..., ge=1, le=8)
    decisions: Decisions | None = None


class OptimizeResponse(BaseModel):
    optimal_decisions: Decisions
    expected_profit: float
    curve_axis: Literal["hot_brew", "cold_brew", "markup", "service_rate"]
    curve: list[CurvePoint]


class ComparisonResponse(BaseModel):
    player_decisions: Decisions
    optimal_decisions: Decisions
    player_expected_profit: float
    optimal_expected_profit: float
    player_realized_profit: float
    optimal_realized_profit: float
    curve_axis: Literal["hot_brew", "cold_brew", "markup", "service_rate"]
    curve: list[CurvePoint]
    metrics: dict[str, float]
    seed: int
    feasible: FeasibilityResult


class SubmitRequest(BaseModel):
    round_number: int = Field(..., ge=1, le=8)
    decisions: Decisions
    session_id: str | None = None
    seed: int | None = None


class SubmitResponse(BaseModel):
    comparison: ComparisonResponse
    submission_id: str | None = None


class ChampionshipCreateRequest(BaseModel):
    match_code: str = Field(..., min_length=3, max_length=20)
    title: str = Field("Class Championship", max_length=120)
    scenario_set_id: str = "default"


class ChampionshipCreateResponse(BaseModel):
    id: str
    match_code: str
    title: str
    scenario_set_id: str


class ChampionshipJoinRequest(BaseModel):
    match_code: str
    display_name: str = Field(..., min_length=1, max_length=40)


class ChampionshipJoinResponse(BaseModel):
    session_id: str
    championship_id: str
    match_code: str
    display_name: str


class LeaderboardEntry(BaseModel):
    display_name: str
    total_realized_profit: float
    rounds_completed: int
    last_submitted_at: str | None = None


class LeaderboardResponse(BaseModel):
    match_code: str
    entries: list[LeaderboardEntry]
