"""
All-time leaderboard endpoint.

GET /api/alltime

Returns each participant's combined W-L record across every season from
2021-22 to the present, sorted by total win percentage (best first).

Data sources:
  - Completed seasons (2021-22 through 2024-25): season_records table in Supabase
  - Current season (2025-26): calculated live from standings_cache + rosters,
    same as the main /api/participants endpoint does

WHY combine them here rather than on the frontend?
  Keeping the aggregation on the backend means the frontend just receives a
  simple sorted list. If you later add more seasons the frontend doesn't change.
"""

from fastapi import APIRouter, HTTPException
from backend.models import AggregateRecord, AllTimeEntry
from backend.services.supabase_client import db
from backend.services import roster_store
from backend.services.standings_store import get_cached_standings

router = APIRouter()

CURRENT_SEASON = "2025-26"

@router.get("/api/alltime")
def get_alltime():
    result = db.table("season_records").select("*").execute()
    records: dict[str, dict[str, tuple[int, int]]] = {}
    for row in result.data:
        records.setdefault(row['participant_name'], {})[row['season']] = (row['wins'], row['losses'])

    all_teams, _ = get_cached_standings()
    rosters = roster_store.load()
    team_map = {t.team_id: t for t in all_teams}
    
    for name, team_ids in rosters.items():
        teams = [team_map[tid] for tid in team_ids if tid in team_map]
        current_wins = sum(t.wins for t in teams)
        current_losses = sum(t.losses for t in teams)
        records.setdefault(name, {})[CURRENT_SEASON] = (current_wins, current_losses)

    entries: list[AllTimeEntry] = []
    for name, seasons in records.items():
        total_wins = sum(w for w, l in seasons.values())
        total_losses = sum(l for w, l in seasons.values())
        total_played = total_wins + total_losses
        win_pct = round(total_wins / total_played, 3) if total_played > 0 else 0.0

        per_season = {season: AggregateRecord(
            wins = w,
            losses = l,
            win_pct = round(w / (w + l), 3) if (w + l) > 0 else 0.0
        )
        for season, (w, l) in seasons.items()}

        entries.append(AllTimeEntry(
            participant_name=name,
            total=AggregateRecord(wins=total_wins, losses=total_losses, win_pct=win_pct),
            per_season=per_season,
        ))    

    entries.sort(key=lambda e: e.total.win_pct, reverse=True)
    return entries
