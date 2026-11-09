# Instructor guide — Coffee Bean Optimization

## Learning goals

1. Feasibility ≠ performance.
2. Single simulation runs are noisy; optimize expected profit.
3. Nonlinear pricing, congestion, and staffing break intuition.
4. Simulation and optimization work together.

## Classroom flow (≈ 60–75 minutes)

1. **Warm-up (5 min):** Open Play mode; explain sliders and Feasible/Infeasible.
2. **Rounds 1–2 (15 min):** Brew decisions only. Ask students to predict before Try Solution.
3. **Rounds 3–4 (10 min):** Introduce brewing cost / waste.
4. **Round 5 (10 min):** Markup reduces demand — sketch the profit hill on the board.
5. **Rounds 6–7 (10 min):** Balking and multi-cup orders; emphasize warm-up vs steady state.
6. **Round 8 (10 min):** Service rate vs wage cost.
7. **Debrief (10 min):** Compare expected vs realized markers on the comparison chart.

## Championship

1. Set `INSTRUCTOR_API_KEY` in `backend/.env`.
2. Open Championship Mode → enter a match code (< 20 chars, case-sensitive) and the API key → Create match.
3. Students join with the same code and a display name.
4. Refresh the leaderboard or Export CSV after submissions.

Scores sum realized 5-day profits across submitted rounds. Students may resubmit a round; the latest submission wins.

## Reproducibility

- Authoritative scoring uses a seeded 120-hour server simulation (`SCORE_HOURS`).
- Scenario parameters live in `backend/app/scenarios/rounds.py`.
- The optimizer maximizes expected profit with a SciPy-free NumPy search.
- Do not claim parity with any commercial teaching game.

## Database

- Local: `docker compose up -d db` applies `supabase/migrations/20260328000000_init.sql`.
- Supabase: paste that SQL into the SQL editor and set `DATABASE_URL` to the pooler URI.
- If the database is unreachable, the API falls back to an in-memory store (fine for demos; not for multi-machine classes).
