import type { SeasonsResponse, StandingsResponse, AllTimeEntry } from "../types";

async function fetchJSON<T>(url: string, options?: RequestInit): Promise<T> {
  const res = await fetch(url, options);
  if (!res.ok) {
    const text = await res.text().catch(() => res.statusText);
    throw new Error(`${res.status} ${text}`);
  }
  return res.json() as Promise<T>;
}

export function fetchParticipants(season: string): Promise<StandingsResponse> {
  return fetchJSON<StandingsResponse>(`/api/participants?season=${encodeURIComponent(season)}`);
}

export function fetchSeasons(): Promise<SeasonsResponse> {
  return fetchJSON<SeasonsResponse>("/api/seasons");
}

export function fetchAllTime(): Promise<AllTimeEntry[]> {
  return fetchJSON<AllTimeEntry[]>("/api/alltime");
}

export function refreshStandings(): Promise<StandingsResponse> {
  return fetchJSON<StandingsResponse>("/api/standings/refresh", { method: "POST" });
}
