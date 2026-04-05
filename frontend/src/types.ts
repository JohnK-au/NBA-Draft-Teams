export interface TeamStats {
  team_id: number;
  name: string;
  abbreviation: string;
  wins: number;
  losses: number;
  home_record: string;
  away_record: string;
  last_10: string;
  conf_rank: number;
  conference: string;
}

export interface AggregateRecord {
  wins: number;
  losses: number;
  win_pct: number;
}

export interface ParticipantStats {
  name: string;
  teams: TeamStats[];
  aggregate: AggregateRecord;
}

export interface SeasonsResponse {
  current: string;
  historical: string[];
}

export interface AllTimeEntry {
  participant_name: string;
  total: AggregateRecord;                      // the headline number — shown prominently
  per_season: Record<string, AggregateRecord>; // season-by-season breakdown
}

export interface StandingsResponse {
  participants: ParticipantStats[];
  fetched_at: string | null;
}
