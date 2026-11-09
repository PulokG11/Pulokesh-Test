import { useEffect, useMemo, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { ComparisonView } from '../components/ComparisonView';
import { Monitors } from '../components/Monitors';
import { ShopCanvas } from '../components/ShopCanvas';
import { SliderPanel } from '../components/SliderPanel';
import { TipCard } from '../components/TipCard';
import { createPlaySession, fetchRounds, submitRound } from '../lib/api';
import { localFeasibility } from '../lib/feasibility';
import type { ComparisonResponse, Decisions, RoundInfo } from '../lib/types';
import { useShopSim } from '../hooks/useShopSim';

export function PlayPage() {
  const [params] = useSearchParams();
  const sessionFromUrl = params.get('session');
  const [rounds, setRounds] = useState<RoundInfo[]>([]);
  const [roundIndex, setRoundIndex] = useState(0);
  const [decisions, setDecisions] = useState<Decisions | null>(null);
  const [tryToken, setTryToken] = useState(0);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [comparison, setComparison] = useState<ComparisonResponse | null>(null);
  const [sessionId, setSessionId] = useState<string | null>(sessionFromUrl);

  const round = rounds[roundIndex] ?? null;
  const feasibility = useMemo(
    () => (round && decisions ? localFeasibility(round, decisions) : null),
    [round, decisions],
  );
  const sim = useShopSim(round, decisions ?? {
    hot_brew: 0,
    cold_brew: 0,
    markup: 0,
    service_rate: 22,
  }, tryToken);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const data = await fetchRounds();
        if (cancelled) return;
        setRounds(data.rounds);
        setDecisions(data.rounds[0].defaults);
        if (!sessionFromUrl) {
          const session = await createPlaySession('Player');
          if (!cancelled) setSessionId(session.session_id);
        }
      } catch (err) {
        if (!cancelled) setError(err instanceof Error ? err.message : 'Failed to load rounds');
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [sessionFromUrl]);

  useEffect(() => {
    if (round) {
      setDecisions(round.defaults);
      setComparison(null);
      setTryToken(0);
    }
  }, [round?.round_number]);

  async function handleSubmit() {
    if (!round || !decisions || !feasibility?.feasible) return;
    setBusy(true);
    setError(null);
    try {
      const result = await submitRound({
        round_number: round.round_number,
        decisions,
        session_id: sessionId,
      });
      setComparison(result.comparison);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Submit failed');
    } finally {
      setBusy(false);
    }
  }

  if (!round || !decisions || !feasibility) {
    return <main className="page">{error ?? 'Loading rounds…'}</main>;
  }

  return (
    <main className="page play-page">
      <header className="play-header">
        <div>
          <p className="eyebrow">Round {round.round_number} of 8</p>
          <h1>{round.title}</h1>
          <p>{round.description}</p>
        </div>
        <div className="round-dots">
          {rounds.map((r, idx) => (
            <button
              key={r.round_number}
              type="button"
              className={idx === roundIndex ? 'dot active' : 'dot'}
              onClick={() => setRoundIndex(idx)}
              aria-label={`Go to round ${r.round_number}`}
            />
          ))}
        </div>
      </header>

      {error && <p className="error">{error}</p>}

      {comparison ? (
        <ComparisonView
          comparison={comparison}
          hasNext={roundIndex < rounds.length - 1}
          onReplay={() => setComparison(null)}
          onNext={() => {
            setComparison(null);
            setRoundIndex((i) => Math.min(i + 1, rounds.length - 1));
          }}
        />
      ) : (
        <div className="play-grid">
          <ShopCanvas state={sim.state} speed={sim.speed} onSpeed={sim.setSpeed} />
          <SliderPanel
            round={round}
            decisions={decisions}
            feasibility={feasibility}
            onChange={setDecisions}
            onTry={() => setTryToken((t) => t + 1)}
            onSubmit={handleSubmit}
            busy={busy}
          />
          <Monitors round={round} feasibility={feasibility} />
          <TipCard tip={round.tip} />
        </div>
      )}
    </main>
  );
}
