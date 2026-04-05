"""
Reads and writes live standings to/from the Supabase standings_cache table.

This replaces the in-memory TTLCache in backend/cache.py for the live season.
The key benefit: data survives server restarts and cold starts, so the first
page load after a cold start reads from Supabase (~100ms) instead of hitting
the NBA API (~3-5s).

The two public functions you need to implement:
  - get_cached_standings() → reads from Supabase, returns (teams, fetched_at)
  - save_standings(teams)  → upserts teams into Supabase, returns fetched_at

"Upsert" means INSERT OR UPDATE — if a row with that team_id already exists,
update it in place; if not, insert a new row. This keeps exactly 30 rows in
the table (one per NBA team) rather than appending new rows every refresh.
In SQL this is: INSERT INTO ... ON CONFLICT (team_id) DO UPDATE SET ...
In supabase-py this is: client.table(...).upsert(...).execute()
"""

from datetime import datetime, timezone
from backend.models import TeamStats

from backend.services.supabase_client import db


def get_cached_standings() -> tuple[list[TeamStats], datetime | None]:
    """
    Read all rows from the standings_cache table.

    Returns a tuple: (list_of_TeamStats, fetched_at_timestamp)
    If the table is empty (never been refreshed), returns ([], None).

    """
    result = db.table("standings_cache").select("*").execute()

    if not result.data:
        return [], None
    
    teams = [TeamStats(**row) for row in result.data]
    fetched_at = datetime.fromisoformat(result.data[0]["fetched_at"])

    return teams, fetched_at


def save_standings(teams: list[TeamStats]) -> datetime:
    """
    Upsert the given TeamStats list into the standings_cache table.
    Sets fetched_at to the current UTC time for all rows.
    Returns the fetched_at datetime that was written.
    """
    now = datetime.now(timezone.utc)
    
    rows = []
    for team in teams:
      row = team.model_dump()
      row["fetched_at"] = now.isoformat()
      rows.append(row)

    db.table("standings_cache").upsert(rows, on_conflict="team_id").execute()

    return now