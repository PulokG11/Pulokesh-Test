import { useEffect, useMemo, useRef, useState } from 'react';
import type { Decisions, RoundInfo } from '../lib/types';

export type Customer = {
  id: number;
  wantsHot: boolean;
  x: number;
};

export type ShopSimState = {
  queue: Customer[];
  served: number;
  balked: number;
  stockout: number;
  profit: number;
  hour: number;
  day: number;
  running: boolean;
  hotInv: number;
  coldInv: number;
};

const emptyState = (): ShopSimState => ({
  queue: [],
  served: 0,
  balked: 0,
  stockout: 0,
  profit: 0,
  hour: 0,
  day: 1,
  running: false,
  hotInv: 0,
  coldInv: 0,
});

function mulberry32(seed: number) {
  let t = seed >>> 0;
  return () => {
    t += 0x6d2b79f5;
    let r = Math.imul(t ^ (t >>> 15), 1 | t);
    r ^= r + Math.imul(r ^ (r >>> 7), 61 | r);
    return ((r ^ (r >>> 14)) >>> 0) / 4294967296;
  };
}

function poisson(rand: () => number, lambda: number): number {
  const L = Math.exp(-lambda);
  let k = 0;
  let p = 1;
  do {
    k += 1;
    p *= rand();
  } while (p > L);
  return k - 1;
}

export function useShopSim(round: RoundInfo | null, decisions: Decisions, tryToken: number) {
  const [state, setState] = useState<ShopSimState>(emptyState);
  const [speed, setSpeed] = useState(1);
  const idRef = useRef(1);
  const randRef = useRef(() => Math.random());

  const params = useMemo(() => {
    if (!round) return null;
    const s = round.scenario;
    const markup = round.active_decisions.includes('markup') ? decisions.markup : 0;
    const baseLambda = Number(s.base_lambda ?? 20);
    const sensitivity = Number(s.markup_sensitivity ?? 0.2);
    const lam = s.enable_markup
      ? Math.max(0.05, baseLambda * Math.exp(-sensitivity * Math.max(0, markup)))
      : baseLambda;
    return {
      lam,
      hotProb: Number(s.hot_prob ?? 0.55),
      serviceRate: round.active_decisions.includes('service_rate')
        ? decisions.service_rate
        : Number(s.default_service_rate ?? 22),
      hotQ: round.active_decisions.includes('hot_brew') ? decisions.hot_brew : 0,
      coldQ: round.active_decisions.includes('cold_brew') ? decisions.cold_brew : 0,
      hotPrice: Number(s.base_price_hot ?? 3) + markup,
      coldPrice: Number(s.base_price_cold ?? 3.5) + markup,
      hotCost: Number(s.hot_cost ?? 0),
      coldCost: Number(s.cold_cost ?? 0),
      enableBalking: Boolean(s.enable_balking),
      balkScale: Number(s.balk_scale ?? 8),
      enableMultiCup: Boolean(s.enable_multi_cup),
      baristaCost: s.enable_service_decision
        ? Number(s.barista_base_cost ?? 0) +
          Number(s.barista_cost_slope ?? 0) *
            (round.active_decisions.includes('service_rate')
              ? decisions.service_rate
              : Number(s.default_service_rate ?? 22))
        : 0,
      hasCold: round.active_decisions.includes('cold_brew'),
    };
  }, [round, decisions]);

  useEffect(() => {
    if (!round || !params || tryToken === 0) return;
    randRef.current = mulberry32(1000 + tryToken * 17 + round.round_number);
    idRef.current = 1;
    setState({
      ...emptyState(),
      running: true,
      hotInv: params.hotQ,
      coldInv: params.coldQ,
    });
  }, [tryToken, round, params]);

  useEffect(() => {
    if (!params || !state.running) return;
    const handle = window.setInterval(() => {
      setState((prev) => {
        if (!prev.running) return prev;
        const rand = randRef.current;
        let queue = [...prev.queue];
        let hotInv = params.hotQ;
        let coldInv = params.coldQ;
        let profit = prev.profit - params.hotCost * params.hotQ - params.coldCost * params.coldQ - params.baristaCost;
        let served = prev.served;
        let balked = prev.balked;
        let stockout = prev.stockout;

        const arrivals = poisson(rand, params.lam / 6); // tick ~10 min
        for (let i = 0; i < arrivals; i += 1) {
          if (params.enableBalking) {
            const pBalk = 1 - Math.exp(-queue.length / params.balkScale);
            if (rand() < pBalk) {
              balked += 1;
              continue;
            }
          }
          queue.push({
            id: idRef.current,
            wantsHot: rand() < params.hotProb || !params.hasCold,
            x: 40 + queue.length * 28,
          });
          idRef.current += 1;
        }

        const capacity = Math.max(0, poisson(rand, params.serviceRate / 6));
        const toServe = Math.min(queue.length, capacity);
        for (let i = 0; i < toServe; i += 1) {
          const customer = queue.shift();
          if (!customer) break;
          const cups = params.enableMultiCup && rand() > 0.45 ? 2 : 1;
          if (customer.wantsHot) {
            if (hotInv < cups) {
              stockout += 1;
              continue;
            }
            hotInv -= cups;
            profit += params.hotPrice * cups;
            served += 1;
          } else {
            if (coldInv < cups) {
              stockout += 1;
              continue;
            }
            coldInv -= cups;
            profit += params.coldPrice * cups;
            served += 1;
          }
        }

        queue = queue.map((c, idx) => ({ ...c, x: 40 + idx * 28 }));
        const nextHour = prev.hour + 1 / 6;
        const day = Math.min(5, 1 + Math.floor(nextHour / 24));
        return {
          queue,
          served,
          balked,
          stockout,
          profit,
          hour: nextHour,
          day,
          running: true,
          hotInv,
          coldInv,
        };
      });
    }, Math.max(80, 400 / speed));
    return () => window.clearInterval(handle);
  }, [params, state.running, speed]);

  return { state, speed, setSpeed, setState };
}
