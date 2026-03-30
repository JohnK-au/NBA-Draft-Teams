import type { TeamStats } from "../types";

interface Props {
  team: TeamStats;
}

export function TeamRow({ team }: Props) {
  return (
    <tr className="team-row">
      <td className="team-row__name">
        <span className="team-row__abbr">{team.abbreviation}</span>
        <span className="team-row__full">{team.name}</span>
      </td>
      <td className="team-row__record">
        {team.wins}–{team.losses}
      </td>
      <td className="team-row__split">
        <span title="Home">H {team.home_record}</span>
        {" / "}
        <span title="Away">A {team.away_record}</span>
      </td>
      <td className="team-row__l10" title="Last 10 games">
        L10: {team.last_10}
      </td>
      <td className="team-row__standing">
        {team.conf_rank}{ordinal(team.conf_rank)} {team.conference}
      </td>
    </tr>
  );
}

function ordinal(n: number): string {
  const s = ["th", "st", "nd", "rd"];
  const v = n % 100;
  return s[(v - 20) % 10] ?? s[v] ?? s[0] ?? "th";
}
