import type { Decisions, FeasibilityResult, RoundInfo } from '../lib/types';

const LABELS: Record<string, string> = {
  hot_brew: 'Hot brew / hour',
  cold_brew: 'Cold brew / hour',
  markup: 'Price markup',
  service_rate: 'Barista service rate',
};

type Props = {
  round: RoundInfo;
  decisions: Decisions;
  feasibility: FeasibilityResult;
  onChange: (next: Decisions) => void;
  onTry: () => void;
  onSubmit: () => void;
  busy: boolean;
};

export function SliderPanel({
  round,
  decisions,
  feasibility,
  onChange,
  onTry,
  onSubmit,
  busy,
}: Props) {
  return (
    <section className="panel slider-panel">
      <div className="panel-head">
        <h2>Decisions</h2>
        <span className={feasibility.feasible ? 'badge ok' : 'badge bad'}>
          {feasibility.feasible ? 'Feasible' : 'Infeasible'}
        </span>
      </div>
      {round.active_decisions.map((name) => {
        const key = name as keyof Decisions;
        const bounds = round.bounds[name];
        return (
          <label key={name} className="slider-row">
            <div className="slider-meta">
              <span>{LABELS[name] ?? name}</span>
              <strong className={feasibility.feasible ? undefined : 'warn'}>
                {decisions[key].toFixed(bounds.step < 1 ? 1 : 0)}
              </strong>
            </div>
            <input
              type="range"
              min={bounds.min}
              max={bounds.max}
              step={bounds.step}
              value={decisions[key]}
              onChange={(e) =>
                onChange({ ...decisions, [key]: Number(e.target.value) })
              }
            />
          </label>
        );
      })}
      {!feasibility.feasible && (
        <ul className="messages">
          {feasibility.messages.map((m) => (
            <li key={m}>{m}</li>
          ))}
        </ul>
      )}
      <div className="actions">
        <button type="button" className="secondary" onClick={onTry} disabled={busy || !feasibility.feasible}>
          Try Solution
        </button>
        <button type="button" onClick={onSubmit} disabled={busy || !feasibility.feasible}>
          {busy ? 'Scoring…' : 'Submit Solution'}
        </button>
      </div>
    </section>
  );
}
