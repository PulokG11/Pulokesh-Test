export type Decisions = {
  hot_brew: number;
  cold_brew: number;
  markup: number;
  service_rate: number;
};

export type FeasibilityResult = {
  feasible: boolean;
  beans_used: number;
  water_used: number;
  beans_cap: number;
  water_cap: number;
  messages: string[];
};

export type RoundInfo = {
  round_number: number;
  title: string;
  description: string;
  tip: string;
  active_decisions: string[];
  defaults: Decisions;
  bounds: Record<string, { min: number; max: number; step: number }>;
  scenario: Record<string, number | boolean | string>;
  features: Record<string, boolean>;
};

export type CurvePoint = {
  x: number;
  expected_profit: number;
};

export type ComparisonResponse = {
  player_decisions: Decisions;
  optimal_decisions: Decisions;
  player_expected_profit: number;
  optimal_expected_profit: number;
  player_realized_profit: number;
  optimal_realized_profit: number;
  curve_axis: keyof Decisions;
  curve: CurvePoint[];
  metrics: Record<string, number>;
  seed: number;
  feasible: FeasibilityResult;
};

export type LeaderboardEntry = {
  display_name: string;
  total_realized_profit: number;
  rounds_completed: number;
  last_submitted_at: string | null;
};
