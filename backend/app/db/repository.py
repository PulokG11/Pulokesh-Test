from __future__ import annotations

import json
import threading
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from app.db.database import db_available, get_connection
from app.models.contracts import Decisions, LeaderboardEntry


@dataclass
class MemoryStore:
    championships: dict[str, dict[str, Any]] = field(default_factory=dict)
    sessions: dict[str, dict[str, Any]] = field(default_factory=dict)
    submissions: list[dict[str, Any]] = field(default_factory=list)
    lock: threading.Lock = field(default_factory=threading.Lock)


MEMORY = MemoryStore()


def create_championship(match_code: str, title: str, scenario_set_id: str) -> dict[str, Any]:
    if db_available():
        with get_connection() as conn:
            row = conn.execute(
                """
                insert into championships (match_code, title, scenario_set_id)
                values (%s, %s, %s)
                returning id::text, match_code, title, scenario_set_id
                """,
                (match_code, title, scenario_set_id),
            ).fetchone()
            conn.commit()
            return {
                "id": row[0],
                "match_code": row[1],
                "title": row[2],
                "scenario_set_id": row[3],
            }

    with MEMORY.lock:
        if any(c["match_code"] == match_code for c in MEMORY.championships.values()):
            raise ValueError("Match code already in use")
        champ_id = str(uuid.uuid4())
        record = {
            "id": champ_id,
            "match_code": match_code,
            "title": title,
            "scenario_set_id": scenario_set_id,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "is_active": True,
        }
        MEMORY.championships[champ_id] = record
        return record


def join_championship(match_code: str, display_name: str) -> dict[str, Any]:
    if db_available():
        with get_connection() as conn:
            champ = conn.execute(
                """
                select id::text, match_code from championships
                where match_code = %s and is_active = true
                """,
                (match_code,),
            ).fetchone()
            if champ is None:
                raise KeyError("Championship not found")
            session = conn.execute(
                """
                insert into player_sessions (championship_id, display_name, mode)
                values (%s::uuid, %s, 'class')
                returning id::text
                """,
                (champ[0], display_name),
            ).fetchone()
            conn.commit()
            return {
                "session_id": session[0],
                "championship_id": champ[0],
                "match_code": champ[1],
                "display_name": display_name,
            }

    with MEMORY.lock:
        champ = next(
            (c for c in MEMORY.championships.values() if c["match_code"] == match_code and c["is_active"]),
            None,
        )
        if champ is None:
            raise KeyError("Championship not found")
        session_id = str(uuid.uuid4())
        MEMORY.sessions[session_id] = {
            "id": session_id,
            "championship_id": champ["id"],
            "display_name": display_name,
            "mode": "class",
            "started_at": datetime.now(timezone.utc).isoformat(),
        }
        return {
            "session_id": session_id,
            "championship_id": champ["id"],
            "match_code": match_code,
            "display_name": display_name,
        }


def create_play_session(display_name: str = "Player") -> str:
    if db_available():
        with get_connection() as conn:
            row = conn.execute(
                """
                insert into player_sessions (display_name, mode)
                values (%s, 'play')
                returning id::text
                """,
                (display_name,),
            ).fetchone()
            conn.commit()
            return row[0]

    session_id = str(uuid.uuid4())
    with MEMORY.lock:
        MEMORY.sessions[session_id] = {
            "id": session_id,
            "championship_id": None,
            "display_name": display_name,
            "mode": "play",
            "started_at": datetime.now(timezone.utc).isoformat(),
        }
    return session_id


def save_submission(
    session_id: str,
    round_number: int,
    decisions: Decisions,
    realized_profit: float,
    expected_profit: float,
    optimal_expected_profit: float,
    seed: int,
) -> str:
    if db_available():
        with get_connection() as conn:
            row = conn.execute(
                """
                insert into round_submissions (
                  session_id, round_number, decisions, realized_profit,
                  expected_profit, optimal_expected_profit, seed
                )
                values (%s::uuid, %s, %s::jsonb, %s, %s, %s, %s)
                on conflict (session_id, round_number) do update set
                  decisions = excluded.decisions,
                  realized_profit = excluded.realized_profit,
                  expected_profit = excluded.expected_profit,
                  optimal_expected_profit = excluded.optimal_expected_profit,
                  seed = excluded.seed,
                  submitted_at = now()
                returning id::text
                """,
                (
                    session_id,
                    round_number,
                    json.dumps(decisions.model_dump()),
                    realized_profit,
                    expected_profit,
                    optimal_expected_profit,
                    seed,
                ),
            ).fetchone()
            conn.commit()
            return row[0]

    with MEMORY.lock:
        if session_id not in MEMORY.sessions:
            raise KeyError("Session not found")
        MEMORY.submissions = [
            s
            for s in MEMORY.submissions
            if not (s["session_id"] == session_id and s["round_number"] == round_number)
        ]
        submission_id = str(uuid.uuid4())
        MEMORY.submissions.append(
            {
                "id": submission_id,
                "session_id": session_id,
                "round_number": round_number,
                "decisions": decisions.model_dump(),
                "realized_profit": realized_profit,
                "expected_profit": expected_profit,
                "optimal_expected_profit": optimal_expected_profit,
                "seed": seed,
                "submitted_at": datetime.now(timezone.utc).isoformat(),
            }
        )
        return submission_id


def leaderboard(match_code: str) -> list[LeaderboardEntry]:
    if db_available():
        with get_connection() as conn:
            rows = conn.execute(
                """
                select display_name, total_realized_profit, rounds_completed,
                       last_submitted_at::text
                from championship_leaderboard
                where match_code = %s
                order by total_realized_profit desc, display_name asc
                """,
                (match_code,),
            ).fetchall()
            return [
                LeaderboardEntry(
                    display_name=r[0],
                    total_realized_profit=float(r[1]),
                    rounds_completed=int(r[2]),
                    last_submitted_at=r[3],
                )
                for r in rows
            ]

    with MEMORY.lock:
        champ = next(
            (c for c in MEMORY.championships.values() if c["match_code"] == match_code),
            None,
        )
        if champ is None:
            raise KeyError("Championship not found")
        sessions = [s for s in MEMORY.sessions.values() if s["championship_id"] == champ["id"]]
        entries: list[LeaderboardEntry] = []
        for session in sessions:
            subs = [s for s in MEMORY.submissions if s["session_id"] == session["id"]]
            total = sum(s["realized_profit"] for s in subs)
            last = max((s["submitted_at"] for s in subs), default=None)
            entries.append(
                LeaderboardEntry(
                    display_name=session["display_name"],
                    total_realized_profit=float(total),
                    rounds_completed=len(subs),
                    last_submitted_at=last,
                )
            )
        entries.sort(key=lambda e: (-e.total_realized_profit, e.display_name))
        return entries
