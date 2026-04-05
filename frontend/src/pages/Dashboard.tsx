import { useState } from "react";
import { useParticipants } from "../hooks/useParticipants";
import { ParticipantCard } from "../components/ParticipantCard";
import { SeasonSelector } from "../components/SeasonSelector";

const CURRENT_SEASON = "2025-26";

export function Dashboard() {
  const [season, setSeason] = useState(CURRENT_SEASON);
  const { participants, loading, error, fetchedAt, refreshing, refresh } = useParticipants(season);

  return (
    <div className="dashboard">
      <header className="dashboard__header">
        <h1>NBA Draft: Team Tracker</h1>
        <SeasonSelector selected={season} onChange={setSeason} />

        {season === CURRENT_SEASON && (
          <div className="dashboard__controls">
            {fetchedAt && (
              <span className="dashboard__last-updated">
                Last updated: {new Date(fetchedAt).toLocaleString()}
              </span>
            )}
            <button onClick={refresh} disabled={refreshing}>
              {refreshing ? "Fetching..." : "Fetch Live Standings"}
            </button>
          </div>
        )}
      </header>

      <main className="dashboard__main">
        {loading && (
          <div className="status-message">
            <p>Loading standings...</p>
          </div>
        )}

        {error && (
          <div className="status-message status-message--error">
            <p>Failed to load data: {error}</p>
            <p className="status-message__sub">Try refreshing the page.</p>
          </div>
        )}

        {!loading && !error && participants.length === 0 && (
          <div className="status-message">
            <p>No rosters configured yet.</p>
          </div>
        )}

        {!loading &&
          !error &&
          participants.map((p, i) => (
            <ParticipantCard key={p.name} participant={p} rank={i + 1} />
          ))}
      </main>
    </div>
  );
}
