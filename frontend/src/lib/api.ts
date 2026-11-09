import type {
  ComparisonResponse,
  Decisions,
  LeaderboardEntry,
  RoundInfo,
} from './types';

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000';

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: {
      'Content-Type': 'application/json',
      ...(init?.headers ?? {}),
    },
    ...init,
  });
  if (!response.ok) {
    const detail = await response.text();
    throw new Error(detail || `Request failed (${response.status})`);
  }
  const contentType = response.headers.get('content-type') ?? '';
  if (contentType.includes('application/json')) {
    return response.json() as Promise<T>;
  }
  return response.text() as Promise<T>;
}

export function fetchRounds(): Promise<{ rounds: RoundInfo[] }> {
  return request('/rounds');
}

export function submitRound(body: {
  round_number: number;
  decisions: Decisions;
  session_id?: string | null;
  seed?: number;
}): Promise<{ comparison: ComparisonResponse; submission_id: string | null }> {
  return request('/submit', { method: 'POST', body: JSON.stringify(body) });
}

export function createChampionship(body: {
  match_code: string;
  title: string;
  instructorKey: string;
}): Promise<{ id: string; match_code: string; title: string }> {
  return request('/championships', {
    method: 'POST',
    headers: { 'X-Instructor-Key': body.instructorKey },
    body: JSON.stringify({
      match_code: body.match_code,
      title: body.title,
      scenario_set_id: 'default',
    }),
  });
}

export function joinChampionship(body: {
  match_code: string;
  display_name: string;
}): Promise<{
  session_id: string;
  championship_id: string;
  match_code: string;
  display_name: string;
}> {
  return request('/championships/join', {
    method: 'POST',
    body: JSON.stringify(body),
  });
}

export function fetchLeaderboard(matchCode: string): Promise<{
  match_code: string;
  entries: LeaderboardEntry[];
}> {
  return request(`/championships/${encodeURIComponent(matchCode)}/leaderboard`);
}

export async function exportLeaderboard(
  matchCode: string,
  instructorKey: string,
): Promise<string> {
  return request(`/championships/${encodeURIComponent(matchCode)}/export`, {
    headers: { 'X-Instructor-Key': instructorKey },
  });
}

export function createPlaySession(displayName = 'Player'): Promise<{
  session_id: string;
}> {
  return request(`/championships/play-session?display_name=${encodeURIComponent(displayName)}`, {
    method: 'POST',
  });
}
