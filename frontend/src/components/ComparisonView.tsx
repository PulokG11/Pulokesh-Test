import type { ComparisonResponse } from '../lib/types';

type Props = {
  comparison: ComparisonResponse;
  onNext: () => void;
  onReplay: () => void;
  hasNext: boolean;
};

export function ComparisonView({ comparison, onNext, onReplay, hasNext }: Props) {
  const maxY = Math.max(
    ...comparison.curve.map((p) => p.expected_profit),
    comparison.player_expected_profit,
    comparison.optimal_expected_profit,
    1,
  );
  const minY = Math.min(...comparison.curve.map((p) => p.expected_profit), 0);
  const width = 560;
  const height = 220;
  const pad = 24;

  const xScale = (x: number) => {
    const xs = comparison.curve.map((p) => p.x);
    const lo = Math.min(...xs);
    const hi = Math.max(...xs);
    return pad + ((x - lo) / Math.max(hi - lo, 1e-6)) * (width - 2 * pad);
  };
  const yScale = (y: number) => {
    return height - pad - ((y - minY) / Math.max(maxY - minY, 1e-6)) * (height - 2 * pad);
  };

  const path = comparison.curve
    .map((p, i) => `${i === 0 ? 'M' : 'L'} ${xScale(p.x)} ${yScale(p.expected_profit)}`)
    .join(' ');

  const playerX = comparison.player_decisions[comparison.curve_axis];
  const optX = comparison.optimal_decisions[comparison.curve_axis];

  return (
    <section className="panel comparison">
      <div className="panel-head">
        <h2>Round Comparison</h2>
        <span className="muted">Seed {comparison.seed}</span>
      </div>
      <div className="compare-grid">
        <div>
          <h3>Your plan</h3>
          <p>Expected {comparison.player_expected_profit.toFixed(1)}</p>
          <p>Realized 5-day {comparison.player_realized_profit.toFixed(1)}</p>
        </div>
        <div>
          <h3>Optimizer</h3>
          <p>Expected {comparison.optimal_expected_profit.toFixed(1)}</p>
          <p>Realized 5-day {comparison.optimal_realized_profit.toFixed(1)}</p>
        </div>
      </div>
      <svg viewBox={`0 0 ${width} ${height}`} className="curve-svg">
        <path d={path} fill="none" stroke="#2f4a3a" strokeWidth="3" />
        <circle
          cx={xScale(playerX)}
          cy={yScale(comparison.player_expected_profit)}
          r="7"
          fill="#c4724a"
        />
        <circle
          cx={xScale(optX)}
          cy={yScale(comparison.optimal_expected_profit)}
          r="7"
          fill="#2f6f8f"
        />
        <circle
          cx={xScale(playerX)}
          cy={yScale(comparison.player_realized_profit)}
          r="5"
          fill="none"
          stroke="#c4724a"
          strokeWidth="2"
        />
        <circle
          cx={xScale(optX)}
          cy={yScale(comparison.optimal_realized_profit)}
          r="5"
          fill="none"
          stroke="#2f6f8f"
          strokeWidth="2"
        />
      </svg>
      <p className="muted">
        Axis: {comparison.curve_axis}. Filled markers = expected profit; hollow = this simulation
        run. Beating the optimizer on one run is luck—expected value is the teaching target.
      </p>
      <div className="actions">
        <button type="button" className="secondary" onClick={onReplay}>
          Replay round
        </button>
        {hasNext && (
          <button type="button" onClick={onNext}>
            Next round
          </button>
        )}
      </div>
    </section>
  );
}
