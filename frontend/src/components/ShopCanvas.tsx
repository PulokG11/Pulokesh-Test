import type { ShopSimState } from '../hooks/useShopSim';

type Props = {
  state: ShopSimState;
  speed: number;
  onSpeed: (n: number) => void;
};

export function ShopCanvas({ state, speed, onSpeed }: Props) {
  return (
    <section className="panel shop-panel">
      <div className="panel-head">
        <h2>Coffee Shop Floor</h2>
        <div className="sim-controls">
          <span>
            Day {state.day} · {state.hour.toFixed(1)}h
          </span>
          <label>
            Speed
            <select value={speed} onChange={(e) => onSpeed(Number(e.target.value))}>
              <option value={1}>1×</option>
              <option value={2}>2×</option>
              <option value={4}>4×</option>
            </select>
          </label>
        </div>
      </div>
      <svg viewBox="0 0 720 280" className="shop-svg" role="img" aria-label="Coffee shop simulation">
        <defs>
          <linearGradient id="floor" x1="0" x2="0" y1="0" y2="1">
            <stop offset="0%" stopColor="#f3ebe0" />
            <stop offset="100%" stopColor="#e4d3bc" />
          </linearGradient>
        </defs>
        <rect width="720" height="280" fill="url(#floor)" rx="18" />
        <rect x="480" y="40" width="200" height="120" rx="12" fill="#2f4a3a" />
        <text x="500" y="70" fill="#f7f1e6" fontSize="16" fontFamily="Georgia, serif">
          Brew Station
        </text>
        <text x="500" y="100" fill="#d9c7a8" fontSize="13">
          Hot {state.hotInv.toFixed(0)} · Cold {state.coldInv.toFixed(0)}
        </text>
        <circle cx="420" cy="150" r="28" fill="#c4724a" />
        <text x="404" y="155" fill="#fff" fontSize="12">
          Barista
        </text>
        <line x1="40" y1="210" x2="400" y2="210" stroke="#8a7355" strokeWidth="4" />
        {state.queue.map((c) => (
          <g key={c.id}>
            <circle cx={c.x} cy="180" r="14" fill={c.wantsHot ? '#b33c1a' : '#2f6f8f'} />
            <text x={c.x - 5} y="160" fontSize="14">
              {c.wantsHot ? '♨' : '❄'}
            </text>
          </g>
        ))}
      </svg>
      <div className="metric-row">
        <span>Served {state.served}</span>
        <span>Balked {state.balked}</span>
        <span>Stockout {state.stockout}</span>
        <span>Live profit {state.profit.toFixed(0)}</span>
      </div>
    </section>
  );
}
