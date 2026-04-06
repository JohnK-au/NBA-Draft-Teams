// =============================================================================
// All-Time Leaderboard Page
// =============================================================================
// This page shows each participant's combined W-L record across every season
// from 2021-22 to the present (including the current live season).
//
// Layout idea:
//   #1  John        485 - 312   .608   ← total record, large and prominent
//       2021-22     185 - 145   .561   ← season breakdown, smaller below
//       2022-23     200 - 130   .606
//       2023-24     ...
//       2025-26     (live)
//
// The total should be the most eye-catching element — use larger font, bold,
// or a coloured badge (similar to how RecordBadge works on the Dashboard).
// The per-season rows can be collapsed by default and expanded on click,
// or just shown as a smaller table beneath each participant's total.
// =============================================================================

import { useState, useEffect } from "react";
import { fetchAllTime } from "../api/client";
import type { AllTimeEntry } from "../types";
import { RecordBadge } from "../components/RecordBadge";

function formatWinPct(pct: number): string {
  return pct.toFixed(3).replace(/^0/, "");  // "0.608" → ".608"
}

function AllTimeCard({ entry, rank }: { entry: AllTimeEntry; rank: number }) {
  const { participant_name, total, per_season } = entry;
  return (
    <div className="participant-card">
      <div className="participant-card__header">
        <span className="participant-card__rank">{rank}</span>
        <span className="participant-card__name">{participant_name}</span>
        <RecordBadge
          wins={total.wins}
          losses={total.losses}
          winPct={total.win_pct}
          size="lg"
        />
      </div>
      <table className="participant-card__table participant-card__table--centered">
        <thead>
          <tr>
            <th>Season</th>
            <th>W–L</th>
            <th>Win %</th>
          </tr>
        </thead>
        <tbody>
          {Object.entries(per_season).sort().map(([season, record]) => (
            <tr key={season} className="team-row">
              <td>{season}</td>
              <td><RecordBadge wins={record.wins} losses={record.losses} /></td>
              <td className="record-badge__pct">{formatWinPct(record.win_pct)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export function AllTime() {
    const [entries, setEntries] = useState<AllTimeEntry[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
      fetchAllTime()
        .then(setEntries)
        .catch((err) => setError(err.message))
        .finally(() => setLoading(false));
    }, []);

  return (
    <div className="dashboard">
      <header className="dashboard__header">
        <h1>All-Time Standings</h1>
        <p style={{ fontSize: "0.9rem", color: "#9ca3b0" }}>2021-22 through present</p>
      </header>

      <main className="dashboard__main">
        {loading && <div className="status-message"><p>Loading standings...</p></div>}
        {error && <div className="status-message status-message--error"><p>Failed to load data: {error}</p></div>}
        {!loading && !error && entries.map((entry, i) => (
          <AllTimeCard key={entry.participant_name} entry={entry} rank={i + 1} />
        ))}
      </main>
    </div>
  );
}
