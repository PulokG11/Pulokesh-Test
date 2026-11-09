import type { Decisions, FeasibilityResult, RoundInfo } from './types';

export function localFeasibility(round: RoundInfo, decisions: Decisions): FeasibilityResult {
  const s = round.scenario;
  const hot = round.active_decisions.includes('hot_brew') ? decisions.hot_brew : 0;
  const cold = round.active_decisions.includes('cold_brew') ? decisions.cold_brew : 0;
  const beansUsed =
    hot * Number(s.beans_per_hot ?? 1) + cold * Number(s.beans_per_cold ?? 1.2);
  const waterUsed =
    hot * Number(s.water_per_hot ?? 1) + cold * Number(s.water_per_cold ?? 0.8);
  const beansCap = Number(s.beans_cap ?? 0);
  const waterCap = Number(s.water_cap ?? 0);
  const messages: string[] = [];
  if (beansUsed > beansCap + 1e-9) {
    messages.push(`Beans needed (${beansUsed.toFixed(1)}) exceed capacity (${beansCap.toFixed(1)}).`);
  }
  if (waterUsed > waterCap + 1e-9) {
    messages.push(`Water needed (${waterUsed.toFixed(1)}) exceed capacity (${waterCap.toFixed(1)}).`);
  }
  return {
    feasible: messages.length === 0,
    beans_used: beansUsed,
    water_used: waterUsed,
    beans_cap: beansCap,
    water_cap: waterCap,
    messages,
  };
}
