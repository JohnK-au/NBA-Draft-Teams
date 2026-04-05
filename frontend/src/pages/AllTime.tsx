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

function formatWinPct(pct: number): string {
  return pct.toFixed(3).replace(/^0/, "");  // "0.608" → ".608"
}

function AllTimeCard({ entry, rank }: { entry: AllTimeEntry; rank: number }) {
  const { participant_name, total, per_season } = entry;
  return (
    <div className="participant-card">
      <div className="participant-card__header">
        <span className="participant-card__rank">#{rank}</span>
        <span className="participant-card__name">{participant_name}</span>
        <span>
          {total.wins}–{total.losses} {formatWinPct(total.win_pct)}
        </span>
      </div>
      <table className="participant-card__table">
        <tbody>
          {Object.entries(per_season).sort().map(([season, record]) => (
            <tr key={season}>
              <td>{season}</td>
              <td>{record.wins}–{record.losses}</td>
              <td>{formatWinPct(record.win_pct)}</td>
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
    <div className="alltime">
      <header className="alltime__header">
        <h1>All-Time Standings</h1>
        <p className="alltime__subtitle">2021-22 through present</p>
      </header>

      <main className="alltime__main">
        {loading && <p>Loading...</p>}
        {error && <p>Error: {error}</p>}
        {!loading && !error && entries.map((entry, i) => (
          <AllTimeCard key={entry.participant_name} entry={entry} rank={i + 1} />
        ))}
      </main>
    </div>
  );
}
