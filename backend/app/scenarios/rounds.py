from __future__ import annotations

from dataclasses import asdict, dataclass, field

from app.models.contracts import Decisions, RoundInfo


@dataclass(frozen=True)
class RoundScenario:
    round_number: int
    title: str
    description: str
    tip: str
    active_decisions: list[str]
    base_lambda: float
    hot_prob: float
    beans_cap: float
    water_cap: float
    beans_per_hot: float = 1.0
    beans_per_cold: float = 1.2
    water_per_hot: float = 1.0
    water_per_cold: float = 0.8
    hot_cost: float = 0.0
    cold_cost: float = 0.0
    base_price_hot: float = 3.0
    base_price_cold: float = 3.5
    markup_sensitivity: float = 0.18
    enable_markup: bool = False
    enable_balking: bool = False
    balk_scale: float = 8.0
    enable_multi_cup: bool = False
    cups_per_customer: float = 1.6
    enable_service_decision: bool = False
    default_service_rate: float = 22.0
    barista_base_cost: float = 8.0
    barista_cost_slope: float = 0.55
    defaults: Decisions = field(default_factory=Decisions)
    bounds: dict[str, dict[str, float]] = field(default_factory=dict)

    def features(self) -> dict[str, bool]:
        return {
            "hot": "hot_brew" in self.active_decisions,
            "cold": "cold_brew" in self.active_decisions,
            "markup": self.enable_markup,
            "balking": self.enable_balking,
            "multi_cup": self.enable_multi_cup,
            "service": self.enable_service_decision,
            "hot_cost": self.hot_cost > 0,
            "cold_cost": self.cold_cost > 0,
        }

    def to_public_dict(self) -> dict:
        data = asdict(self)
        data.pop("defaults")
        data.pop("bounds")
        data.pop("title")
        data.pop("description")
        data.pop("tip")
        data.pop("active_decisions")
        data.pop("round_number")
        return data


def _bounds(*names: str) -> dict[str, dict[str, float]]:
    catalog = {
        "hot_brew": {"min": 0, "max": 60, "step": 1},
        "cold_brew": {"min": 0, "max": 60, "step": 1},
        "markup": {"min": 0, "max": 6, "step": 0.1},
        "service_rate": {"min": 5, "max": 45, "step": 0.5},
    }
    return {name: catalog[name] for name in names}


ROUND_SCENARIOS: dict[int, RoundScenario] = {
    1: RoundScenario(
        round_number=1,
        title="Steam Ahead",
        description="Brew only hot coffee. Learn how under- and over-brewing affect profit.",
        tip="Start near expected demand, then nudge while watching the profit monitor.",
        active_decisions=["hot_brew"],
        base_lambda=28.0,
        hot_prob=1.0,
        beans_cap=40.0,
        water_cap=45.0,
        hot_cost=0.0,
        defaults=Decisions(hot_brew=20, cold_brew=0, markup=0, service_rate=22),
        bounds=_bounds("hot_brew"),
    ),
    2: RoundScenario(
        round_number=2,
        title="Hot and Cold",
        description="Serve both drinks under shared bean and water limits.",
        tip="Feasibility is necessary but not sufficient—balance the two drinks.",
        active_decisions=["hot_brew", "cold_brew"],
        base_lambda=30.0,
        hot_prob=0.55,
        beans_cap=55.0,
        water_cap=50.0,
        defaults=Decisions(hot_brew=16, cold_brew=12, markup=0, service_rate=22),
        bounds=_bounds("hot_brew", "cold_brew"),
    ),
    3: RoundScenario(
        round_number=3,
        title="Waste Costs Money",
        description="Hot coffee now has a brewing cost, so leftovers hurt profit.",
        tip="When cost appears, the best brew quantity usually drops below raw demand.",
        active_decisions=["hot_brew", "cold_brew"],
        base_lambda=30.0,
        hot_prob=0.55,
        beans_cap=55.0,
        water_cap=50.0,
        hot_cost=1.1,
        cold_cost=0.0,
        defaults=Decisions(hot_brew=14, cold_brew=12, markup=0, service_rate=22),
        bounds=_bounds("hot_brew", "cold_brew"),
    ),
    4: RoundScenario(
        round_number=4,
        title="Both Drinks Cost",
        description="Cold coffee is costly too. Over-brewing either drink burns margin.",
        tip="Compare the two profit slices—peaks need not sit at the resource wall.",
        active_decisions=["hot_brew", "cold_brew"],
        base_lambda=30.0,
        hot_prob=0.55,
        beans_cap=55.0,
        water_cap=50.0,
        hot_cost=1.1,
        cold_cost=1.3,
        defaults=Decisions(hot_brew=13, cold_brew=11, markup=0, service_rate=22),
        bounds=_bounds("hot_brew", "cold_brew"),
    ),
    5: RoundScenario(
        round_number=5,
        title="Price Matters",
        description="Choose a markup. Higher prices lift margin but shrink arrivals.",
        tip="Watch how the arrival rate falls as markup rises—profit is nonlinear.",
        active_decisions=["hot_brew", "cold_brew", "markup"],
        base_lambda=32.0,
        hot_prob=0.55,
        beans_cap=55.0,
        water_cap=50.0,
        hot_cost=1.1,
        cold_cost=1.3,
        enable_markup=True,
        markup_sensitivity=0.2,
        defaults=Decisions(hot_brew=12, cold_brew=10, markup=2.0, service_rate=22),
        bounds=_bounds("hot_brew", "cold_brew", "markup"),
    ),
    6: RoundScenario(
        round_number=6,
        title="The Line Walks Away",
        description="Crowded queues make customers balk. Congestion now matters.",
        tip="Let the simulation warm up—early empty-shop metrics are misleading.",
        active_decisions=["hot_brew", "cold_brew", "markup"],
        base_lambda=34.0,
        hot_prob=0.55,
        beans_cap=58.0,
        water_cap=52.0,
        hot_cost=1.1,
        cold_cost=1.3,
        enable_markup=True,
        enable_balking=True,
        balk_scale=7.0,
        defaults=Decisions(hot_brew=12, cold_brew=10, markup=1.8, service_rate=22),
        bounds=_bounds("hot_brew", "cold_brew", "markup"),
    ),
    7: RoundScenario(
        round_number=7,
        title="Bigger Orders",
        description="Customers may order multiple cups, scaling effective demand.",
        tip="A single run can beat the optimum by luck—trust expected profit.",
        active_decisions=["hot_brew", "cold_brew", "markup"],
        base_lambda=30.0,
        hot_prob=0.55,
        beans_cap=70.0,
        water_cap=65.0,
        hot_cost=1.1,
        cold_cost=1.3,
        enable_markup=True,
        enable_balking=True,
        enable_multi_cup=True,
        cups_per_customer=1.7,
        defaults=Decisions(hot_brew=18, cold_brew=14, markup=1.8, service_rate=24),
        bounds=_bounds("hot_brew", "cold_brew", "markup"),
    ),
    8: RoundScenario(
        round_number=8,
        title="Hire the Barista",
        description="Pick service speed. Faster clearing costs more wages.",
        tip="Balance queue loss against barista cost—another nonlinear trade-off.",
        active_decisions=["hot_brew", "cold_brew", "markup", "service_rate"],
        base_lambda=32.0,
        hot_prob=0.55,
        beans_cap=70.0,
        water_cap=65.0,
        hot_cost=1.1,
        cold_cost=1.3,
        enable_markup=True,
        enable_balking=True,
        enable_multi_cup=True,
        cups_per_customer=1.7,
        enable_service_decision=True,
        default_service_rate=24.0,
        barista_base_cost=6.0,
        barista_cost_slope=0.65,
        defaults=Decisions(hot_brew=18, cold_brew=14, markup=1.8, service_rate=24),
        bounds=_bounds("hot_brew", "cold_brew", "markup", "service_rate"),
    ),
}


def get_round(round_number: int) -> RoundScenario:
    if round_number not in ROUND_SCENARIOS:
        raise KeyError(f"Unknown round {round_number}")
    return ROUND_SCENARIOS[round_number]


def list_rounds() -> list[RoundInfo]:
    rounds: list[RoundInfo] = []
    for scenario in ROUND_SCENARIOS.values():
        rounds.append(
            RoundInfo(
                round_number=scenario.round_number,
                title=scenario.title,
                description=scenario.description,
                tip=scenario.tip,
                active_decisions=scenario.active_decisions,
                defaults=scenario.defaults,
                bounds=scenario.bounds,
                scenario=scenario.to_public_dict(),
                features=scenario.features(),
            )
        )
    return rounds
