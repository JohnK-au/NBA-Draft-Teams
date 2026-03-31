import { useState, useEffect } from "react";
import { fetchParticipants } from "../api/client";
import type { ParticipantStats } from "../types";

interface State {
  participants: ParticipantStats[];
  loading: boolean;
  error: string | null;
}

const MOCK_DATA: ParticipantStats[] = [
  {
    name: "John",
    teams: [
      { team_id: 1, name: "Houston Rockets", abbreviation: "HOU", wins: 40, losses: 27, home_record: "22-11", away_record: "18-16", last_10: "7-3", conf_rank: 3, conference: "West" },
      { team_id: 2, name: "Los Angeles Lakers", abbreviation: "LAL", wins: 35, losses: 32, home_record: "20-14", away_record: "15-18", last_10: "5-5", conf_rank: 8, conference: "West" },
    ],
    aggregate: { wins: 75, losses: 59, win_pct: 0.560 },
  },
  {
    name: "Nate",
    teams: [
      { team_id: 3, name: "Denver Nuggets", abbreviation: "DEN", wins: 38, losses: 29, home_record: "21-12", away_record: "17-17", last_10: "6-4", conf_rank: 5, conference: "West" },
      { team_id: 4, name: "Boston Celtics", abbreviation: "BOS", wins: 50, losses: 17, home_record: "27-7", away_record: "23-10", last_10: "8-2", conf_rank: 1, conference: "East" },
    ],
    aggregate: { wins: 88, losses: 46, win_pct: 0.657 },
  },
];

const USE_MOCK = false; // Set to false to use the real backend

export function useParticipants(season: string): State {
  const [state, setState] = useState<State>({
    participants: [],
    loading: true,
    error: null,
  });

  useEffect(() => {
    if (USE_MOCK) {
      setState({ participants: MOCK_DATA, loading: false, error: null });
      return;
    }

    let cancelled = false;
    setState({ participants: [], loading: true, error: null });

    fetchParticipants(season)
      .then((data) => {
        if (!cancelled) setState({ participants: data, loading: false, error: null });
      })
      .catch((err: unknown) => {
        if (!cancelled)
          setState({
            participants: [],
            loading: false,
            error: err instanceof Error ? err.message : "Unknown error",
          });
      });

    return () => {
      cancelled = true;
    };
  }, [season]);

  return state;
}
