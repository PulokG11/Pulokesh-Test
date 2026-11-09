-- Coffee Bean Optimization initial schema (Supabase / Postgres)

create extension if not exists "pgcrypto";

create table if not exists championships (
  id uuid primary key default gen_random_uuid(),
  match_code text not null unique,
  title text not null default 'Class Championship',
  scenario_set_id text not null default 'default',
  created_at timestamptz not null default now(),
  is_active boolean not null default true
);

create table if not exists player_sessions (
  id uuid primary key default gen_random_uuid(),
  championship_id uuid references championships(id) on delete set null,
  display_name text not null,
  mode text not null check (mode in ('play', 'class')),
  started_at timestamptz not null default now()
);

create table if not exists round_submissions (
  id uuid primary key default gen_random_uuid(),
  session_id uuid not null references player_sessions(id) on delete cascade,
  round_number integer not null check (round_number between 1 and 8),
  decisions jsonb not null,
  realized_profit double precision not null,
  expected_profit double precision not null,
  optimal_expected_profit double precision not null,
  seed bigint not null,
  submitted_at timestamptz not null default now(),
  unique (session_id, round_number)
);

create index if not exists idx_player_sessions_championship
  on player_sessions (championship_id);

create index if not exists idx_round_submissions_session
  on round_submissions (session_id);

create or replace view championship_leaderboard as
select
  c.match_code,
  ps.display_name,
  coalesce(sum(rs.realized_profit), 0) as total_realized_profit,
  count(rs.id)::int as rounds_completed,
  max(rs.submitted_at) as last_submitted_at
from championships c
join player_sessions ps on ps.championship_id = c.id
left join round_submissions rs on rs.session_id = ps.id
group by c.match_code, ps.id, ps.display_name;
