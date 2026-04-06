import type { ParticipantStats } from "../types";
import { RecordBadge } from "./RecordBadge";
import { TeamRow } from "./TeamRow";

interface Props {
  participant: ParticipantStats;
  rank: number;
}

export function ParticipantCard({ participant, rank }: Props) {
  const { name, teams, aggregate } = participant;

  return (
    <div className="participant-card">
      <div className="participant-card__header">
        <span className="participant-card__rank">{rank}</span>
        <span className="participant-card__name">{name}</span>
        <RecordBadge
          wins={aggregate.wins}
          losses={aggregate.losses}
          winPct={aggregate.win_pct}
          size="lg"
        />
      </div>

      {teams.length > 0 ? (
        <table className="participant-card__table">
          <thead>
            <tr>
              <th className="th--left">Team</th>
              <th>W–L</th>
              <th>Home / Away</th>
              <th>Last 10</th>
              <th>Standing</th>
            </tr>
          </thead>
          <tbody>
            {teams.map((t) => (
              <TeamRow key={t.team_id} team={t} />
            ))}
          </tbody>
        </table>
      ) : (
        <p className="participant-card__empty">No teams drafted yet.</p>
      )}
    </div>
  );
}
