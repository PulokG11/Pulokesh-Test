# Supabase / Postgres

Apply [`migrations/20260328000000_init.sql`](migrations/20260328000000_init.sql) to your Supabase project (SQL editor) or use local Docker Compose from the repo root:

```bash
docker compose up -d db
```

Then set `DATABASE_URL` in `backend/.env` to the Postgres connection string (Supabase pooler URI or `postgresql://postgres:postgres@localhost:5432/coffee_bean`).
