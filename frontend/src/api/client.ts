import type { ParticipantStats, SeasonsResponse } from "../types";

async function fetchJSON<T>(url: string): Promise<T> {
  const res = await fetch(url);
  if (!res.ok) {
    const text = await res.text().catch(() => res.statusText);
    throw new Error(`${res.status} ${text}`);
  }
  return res.json() as Promise<T>;
}

export function fetchParticipants(season: string): Promise<ParticipantStats[]> {
  return fetchJSON<ParticipantStats[]>(`/api/participants?season=${encodeURIComponent(season)}`);
}

export function fetchSeasons(): Promise<SeasonsResponse> {
  return fetchJSON<SeasonsResponse>("/api/seasons");
}
