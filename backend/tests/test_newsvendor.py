import math

from app.engine.newsvendor import expected_oversell, expected_profit_cup, expected_sales


def test_expected_sales_at_mean_near_half():
    mean = 25.0
    q = 25.0
    sales = expected_sales(q, mean, mean)
    # For symmetric Normal, E[min(Q,D)] at Q=mean is slightly below mean.
    assert 0.4 * mean < sales < mean


def test_oversell_nonnegative():
    assert expected_oversell(10, 20, 20) >= 0
    assert expected_oversell(40, 20, 20) > 0


def test_profit_increases_then_may_fall_with_cost():
    mean = 20.0
    revenue = 3.0
    cost = 1.0
    profits = [expected_profit_cup(q, mean, revenue, cost) for q in range(0, 41)]
    assert max(profits) > profits[0]
    best = max(range(len(profits)), key=lambda i: profits[i])
    assert 5 <= best <= 35


def test_zero_cost_prefers_higher_q_within_reason():
    mean = 20.0
    low = expected_profit_cup(10, mean, 3.0, 0.0)
    high = expected_profit_cup(30, mean, 3.0, 0.0)
    assert high >= low - 1e-9
    assert math.isfinite(high)
