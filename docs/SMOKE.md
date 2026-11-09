# Smoke path (classroom demo)

1. Start database (optional for single-machine memory mode):

```bash
docker compose up -d db
```

2. Start API:

```bash
cd backend
.\.venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --port 8000
```

3. Start UI:

```bash
cd frontend
npm run dev
```

4. Browser checks:

- Home → Play → Try Solution → Submit Solution → see comparison chart.
- Advance through rounds 1–8.
- Championship → create match with instructor key → join in a second browser profile → submit → export CSV.

5. API health:

```bash
curl http://127.0.0.1:8000/health
```
