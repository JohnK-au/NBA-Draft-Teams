import { useState, useEffect } from "react";
import { fetchParticipants } from "../api/client";
import type { ParticipantStats } from "../types";

interface State {
  participants: ParticipantStats[];
  loading: boolean;
  error: string | null;
}

export function useParticipants(season: string): State {
  const [state, setState] = useState<State>({
    participants: [],
    loading: true,
    error: null,
  });

  useEffect(() => {
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
