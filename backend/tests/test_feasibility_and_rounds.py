from app.engine.feasibility import check_feasibility
from app.engine.expected import expected_profit_for_decisions
from app.engine.optimizer import optimize_round
from app.engine.des import simulate_shop
from app.models.contracts import Decisions
from app.scenarios.rounds import get_round, list_rounds


def test_eight_rounds_defined():
    rounds = list_rounds()
    assert len(rounds) == 8
    assert [r.round_number for r in rounds] == list(range(1, 9))


def test_infeasible_when_over_beans():
    scenario = get_round(2)
    decisions = Decisions(hot_brew=60, cold_brew=60, markup=0, service_rate=22)
    result = check_feasibility(scenario, decisions)
    assert not result.feasible
    assert result.beans_used > result.beans_cap


def test_feasible_defaults():
    for n in range(1, 9):
        scenario = get_round(n)
        result = check_feasibility(scenario, scenario.defaults)
        assert result.feasible, f"round {n} defaults should be feasible"


def test_seeded_simulation_reproducible():
    scenario = get_round(2)
    decisions = scenario.defaults
    a = simulate_shop(scenario, decisions, hours=48, seed=123)
    b = simulate_shop(scenario, decisions, hours=48, seed=123)
    assert a.realized_profit == b.realized_profit
    assert a.metrics["customers_arrived"] == b.metrics["customers_arrived"]


def test_optimizer_beats_naive_low_brew_round1():
    scenario = get_round(1)
    optimal, optimal_profit = optimize_round(scenario)
    naive = Decisions(hot_brew=1, cold_brew=0, markup=0, service_rate=22)
    naive_profit = expected_profit_for_decisions(scenario, naive)
    assert optimal_profit >= naive_profit
    assert optimal.hot_brew > 1
