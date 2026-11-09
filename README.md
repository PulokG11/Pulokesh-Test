# Coffee Bean Optimization

Original classroom game for teaching nonlinear / stochastic optimization through a coffee-shop simulation.

Players choose brewing rates, markup, and barista speed across **8 progressive rounds**, watch a live shop simulation, and compare their decisions to an expected-profit optimum. Class championships use shareable match codes and instructor score export.

This is an **independent educational implementation** inspired by publicly documented operations-research teaching concepts (newsvendor inventory, queueing, simulation under uncertainty). It is **not affiliated with Gurobi**, and it does **not** use Gurobi trademarks, art, audio, or proprietary client code.

## Live deploy

| Service | URL |
|---------|-----|
| **Play the game (Netlify)** | [https://coffee-bean-optimization.netlify.app](https://coffee-bean-optimization.netlify.app) |
| **API home (Vercel)** | [https://coffee-bean-api-two.vercel.app](https://coffee-bean-api-two.vercel.app) |
| **API docs (Swagger)** | [https://coffee-bean-api-two.vercel.app/docs](https://coffee-bean-api-two.vercel.app/docs) |
| **API health check** | [https://coffee-bean-api-two.vercel.app/health](https://coffee-bean-api-two.vercel.app/health) |
| **GitHub repository** | [https://github.com/PulokG11/Pulokesh-Test](https://github.com/PulokG11/Pulokesh-Test) |

> The Vercel URL is the **backend API** (JSON / OpenAPI), not the game UI. Use the Netlify link to play.

## How to play

Start here: **[docs/HOW_TO_PLAY.md](docs/HOW_TO_PLAY.md)** — detailed player guide covering controls, the submit/compare loop, all eight rounds, championships, and scoring tips.

## Stack

- **Frontend:** React + TypeScript (Vite)
- **Backend:** FastAPI + Python (NumPy + SciPy-free expected-profit optimizer)
- **Database:** PostgreSQL (Supabase-compatible migrations; local Docker Compose included)

## Quick start (local)

### 1. Database

```bash
docker compose up -d db
```

Or create a Supabase project and apply [`supabase/migrations/20260328000000_init.sql`](supabase/migrations/20260328000000_init.sql) in the SQL editor. Set `DATABASE_URL` to the pooler connection string.

### 2. Backend

```bash
cd backend
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1   # Windows PowerShell
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload --port 8000
```

### 3. Frontend

```bash
cd frontend
npm install
copy .env.example .env
npm run dev
```

Open http://localhost:5173

### Instructor championships

1. Set `INSTRUCTOR_API_KEY` in `backend/.env` (or the deployed API environment).
2. Open the live site → **Championship** → create a match with the API key + match code.
3. Students join with the match code and a display name.
4. Export scores with the same instructor key.

## Round progression

| Round | Decisions | New effect |
|------:|-----------|------------|
| 1 | Hot brew qty | Newsvendor intuition |
| 2 | Hot + cold brew | Two products, beans/water |
| 3 | + hot brew cost | Waste costs money |
| 4 | + cold brew cost | Both costly |
| 5 | + markup | Demand falls with price |
| 6 | + balking | Queue congestion / lost customers |
| 7 | + multi-cup orders | Scaled demand |
| 8 | + barista service rate | Wage vs throughput |

## Reproducibility

- Authoritative scoring runs a seeded **120-hour (5-day)** simulation on the server.
- The optimizer maximizes **expected** profit (closed-form newsvendor early; coordinate search later), not one lucky run.
- Scenario parameters live in [`backend/app/scenarios/rounds.py`](backend/app/scenarios/rounds.py) so instructors can tune classroom difficulty.
- Scores are **not** claimed to match any third-party commercial game.

## Tests

```bash
cd backend
pytest -q
```

## Docs

- [docs/HOW_TO_PLAY.md](docs/HOW_TO_PLAY.md) — player guide
- [docs/INSTRUCTOR.md](docs/INSTRUCTOR.md) — lesson arc, championships, reproducibility
- [docs/SMOKE.md](docs/SMOKE.md) — end-to-end classroom smoke path

## Academic use

Intended for classroom teaching and academic research. Preserve attribution in the README when redistributing. Do not ship Gurobi branding or assets.
