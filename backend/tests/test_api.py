from fastapi.testclient import TestClient

from app.main import app
from app.db.repository import MEMORY


client = TestClient(app)


def setup_function() -> None:
    MEMORY.championships.clear()
    MEMORY.sessions.clear()
    MEMORY.submissions.clear()


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_rounds_list():
    response = client.get("/rounds")
    assert response.status_code == 200
    assert len(response.json()["rounds"]) == 8


def test_simulate_and_submit_round1():
    body = {
        "round_number": 1,
        "decisions": {"hot_brew": 20, "cold_brew": 0, "markup": 0, "service_rate": 22},
        "seed": 7,
        "hours": 24,
    }
    sim = client.post("/simulate", json=body)
    assert sim.status_code == 200
    assert sim.json()["feasible"]["feasible"] is True

    submitted = client.post(
        "/submit",
        json={
            "round_number": 1,
            "decisions": body["decisions"],
            "seed": 7,
        },
    )
    assert submitted.status_code == 200
    comparison = submitted.json()["comparison"]
    assert "optimal_decisions" in comparison
    assert len(comparison["curve"]) > 5


def test_championship_flow_memory():
    created = client.post(
        "/championships",
        json={"match_code": "ClassA1", "title": "Demo"},
        headers={"X-Instructor-Key": "change-me-instructor-key"},
    )
    assert created.status_code == 200

    joined = client.post(
        "/championships/join",
        json={"match_code": "ClassA1", "display_name": "Ada"},
    )
    assert joined.status_code == 200
    session_id = joined.json()["session_id"]

    submitted = client.post(
        "/submit",
        json={
            "round_number": 1,
            "session_id": session_id,
            "seed": 1,
            "decisions": {"hot_brew": 18, "cold_brew": 0, "markup": 0, "service_rate": 22},
        },
    )
    assert submitted.status_code == 200
    assert submitted.json()["submission_id"]

    board = client.get("/championships/ClassA1/leaderboard")
    assert board.status_code == 200
    assert board.json()["entries"][0]["display_name"] == "Ada"

    export = client.get(
        "/championships/ClassA1/export",
        headers={"X-Instructor-Key": "change-me-instructor-key"},
    )
    assert export.status_code == 200
    assert "Ada" in export.text
