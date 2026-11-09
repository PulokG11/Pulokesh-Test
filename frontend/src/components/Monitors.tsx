import type { FeasibilityResult, RoundInfo } from '../lib/types';

type Props = {
  round: RoundInfo;
  feasibility: FeasibilityResult;
};

export function Monitors({ round, feasibility }: Props) {
  const beanPct = Math.min(100, (feasibility.beans_used / Math.max(feasibility.beans_cap, 1)) * 100);
  const waterPct = Math.min(100, (feasibility.water_used / Math.max(feasibility.water_cap, 1)) * 100);

  return (
    <section className="panel monitors">
      <div>
        <h2>Constraint Monitor</h2>
        <div className="bar-block">
          <div className="bar-label">
            <span>Beans</span>
            <span>
              {feasibility.beans_used.toFixed(1)} / {feasibility.beans_cap.toFixed(1)}
            </span>
          </div>
          <div className="bar-track">
            <div
              className={`bar-fill ${beanPct > 100 || !feasibility.feasible ? 'over' : ''}`}
              style={{ width: `${Math.min(beanPct, 100)}%` }}
            />
          </div>
        </div>
        <div className="bar-block">
          <div className="bar-label">
            <span>Water</span>
            <span>
              {feasibility.water_used.toFixed(1)} / {feasibility.water_cap.toFixed(1)}
            </span>
          </div>
          <div className="bar-track">
            <div
              className={`bar-fill water ${waterPct > 100 || !feasibility.feasible ? 'over' : ''}`}
              style={{ width: `${Math.min(waterPct, 100)}%` }}
            />
          </div>
        </div>
      </div>
      <div>
        <h2>Profit Monitor</h2>
        <p className="muted">
          Round {round.round_number}: expected profit curves appear after you submit. While
          experimenting, watch live profit on the shop floor and keep decisions feasible.
        </p>
        <div className="hint-card">
          Active levers: {round.active_decisions.join(', ')}
        </div>
      </div>
    </section>
  );
}
