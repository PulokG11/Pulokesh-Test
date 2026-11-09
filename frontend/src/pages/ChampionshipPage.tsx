import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import {
  createChampionship,
  exportLeaderboard,
  fetchLeaderboard,
  joinChampionship,
} from '../lib/api';
import type { LeaderboardEntry } from '../lib/types';

export function ChampionshipPage() {
  const navigate = useNavigate();
  const [matchCode, setMatchCode] = useState('');
  const [displayName, setDisplayName] = useState('');
  const [title, setTitle] = useState('Class Championship');
  const [instructorKey, setInstructorKey] = useState('');
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [entries, setEntries] = useState<LeaderboardEntry[]>([]);

  async function handleCreate() {
    setError(null);
    setMessage(null);
    try {
      const created = await createChampionship({
        match_code: matchCode,
        title,
        instructorKey,
      });
      setMessage(`Created match ${created.match_code}. Share it with your class.`);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Create failed');
    }
  }

  async function handleJoin() {
    setError(null);
    setMessage(null);
    try {
      const joined = await joinChampionship({
        match_code: matchCode,
        display_name: displayName,
      });
      navigate(`/play?session=${joined.session_id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Join failed');
    }
  }

  async function handleLeaderboard() {
    setError(null);
    try {
      const board = await fetchLeaderboard(matchCode);
      setEntries(board.entries);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Leaderboard failed');
    }
  }

  async function handleExport() {
    setError(null);
    try {
      const csv = await exportLeaderboard(matchCode, instructorKey);
      const blob = new Blob([csv], { type: 'text/csv' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${matchCode}-leaderboard.csv`;
      a.click();
      URL.revokeObjectURL(url);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Export failed');
    }
  }

  return (
    <main className="page championship-page">
      <header>
        <p className="eyebrow">Classroom competition</p>
        <h1>Championship Mode</h1>
        <p>Create a private match code for your class, or join one with a display name.</p>
        <Link to="/">← Back home</Link>
      </header>

      {error && <p className="error">{error}</p>}
      {message && <p className="ok-msg">{message}</p>}

      <div className="champ-grid">
        <section className="panel">
          <h2>Join a match</h2>
          <label>
            Match code
            <input value={matchCode} onChange={(e) => setMatchCode(e.target.value)} />
          </label>
          <label>
            Display name
            <input value={displayName} onChange={(e) => setDisplayName(e.target.value)} />
          </label>
          <button type="button" onClick={handleJoin} disabled={!matchCode || !displayName}>
            Join and play
          </button>
        </section>

        <section className="panel">
          <h2>Instructor tools</h2>
          <label>
            Match code
            <input value={matchCode} onChange={(e) => setMatchCode(e.target.value)} />
          </label>
          <label>
            Title
            <input value={title} onChange={(e) => setTitle(e.target.value)} />
          </label>
          <label>
            Instructor API key
            <input
              type="password"
              value={instructorKey}
              onChange={(e) => setInstructorKey(e.target.value)}
            />
          </label>
          <div className="actions">
            <button type="button" onClick={handleCreate} disabled={!matchCode || !instructorKey}>
              Create match
            </button>
            <button type="button" className="secondary" onClick={handleLeaderboard} disabled={!matchCode}>
              Refresh board
            </button>
            <button
              type="button"
              className="secondary"
              onClick={handleExport}
              disabled={!matchCode || !instructorKey}
            >
              Export CSV
            </button>
          </div>
        </section>
      </div>

      {entries.length > 0 && (
        <section className="panel">
          <h2>Leaderboard</h2>
          <table>
            <thead>
              <tr>
                <th>Player</th>
                <th>Total profit</th>
                <th>Rounds</th>
                <th>Last submit</th>
              </tr>
            </thead>
            <tbody>
              {entries.map((e) => (
                <tr key={e.display_name + String(e.last_submitted_at)}>
                  <td>{e.display_name}</td>
                  <td>{e.total_realized_profit.toFixed(1)}</td>
                  <td>{e.rounds_completed}</td>
                  <td>{e.last_submitted_at ?? '—'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </section>
      )}
    </main>
  );
}
