import { useState } from "react";
import { useParticipants } from "../hooks/useParticipants";
import { ParticipantCard } from "../components/ParticipantCard";
import { SeasonSelector } from "../components/SeasonSelector";

const CURRENT_SEASON = "2025-26";

export function Dashboard() {
  const [season, setSeason] = useState(CURRENT_SEASON);
  const { participants, loading, error } = useParticipants(season);

  return (
    <div className="dashboard">
      <header className="dashboard__header">
        <h1>NBA Draft: Team Tracker</h1>
        <SeasonSelector selected={season} onChange={setSeason} />
      </header>

      <main className="dashboard__main">
        {loading && (
          <div className="status-message">
            <p>Loading standings...</p>
            <p className="status-message__sub">
              (First load may take ~30s if the server is waking up)
            </p>
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
