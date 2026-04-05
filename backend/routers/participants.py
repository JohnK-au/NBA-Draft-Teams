from fastapi import APIRouter, HTTPException, Query
from backend.services import roster_store, historical, standings_store
from backend.services.nba_client import fetch_and_store_live_standings
from backend.models import ParticipantStats, AggregateRecord, TeamStats, StandingsResponse

router = APIRouter()

CURRENT_SEASON = "2025-26"


def _build_participants(
    rosters: dict[str, list[int]],
    all_teams: list[TeamStats],
) -> list[ParticipantStats]:
    team_map = {t.team_id: t for t in all_teams}
    participants: list[ParticipantStats] = []

    for name, team_ids in rosters.items():
        teams = [team_map[tid] for tid in team_ids if tid in team_map]
        total_wins = sum(t.wins for t in teams)
        total_losses = sum(t.losses for t in teams)
        played = total_wins + total_losses
        win_pct = round(total_wins / played, 3) if played > 0 else 0.0

        participants.append(
            ParticipantStats(
                name=name,
                teams=teams,
                aggregate=AggregateRecord(
                    wins=total_wins,
                    losses=total_losses,
                    win_pct=win_pct,
                ),
            )
        )

    # Sort by win percentage descending
    participants.sort(key=lambda p: p.aggregate.win_pct, reverse=True)
    return participants


@router.get("/api/participants", response_model=StandingsResponse)
def get_participants(
    season: str = Query(default=CURRENT_SEASON, description="Season string e.g. '2024-25'"),
):
    rosters = roster_store.load()
    if not rosters:
        return StandingsResponse(participants=[], fetched_at=None)
    
    available_historical = historical.list_seasons()
    fetched_at = None

    if season == CURRENT_SEASON:
        try:
            all_teams, fetched_at = standings_store.get_cached_standings()
            if not all_teams:
                # Cache is empty (first ever run) - seed it from the NBA API
                fetch_and_store_live_standings()
                all_teams, fetched_at = standings_store.get_cached_standings()
        except RuntimeError as exc:
            raise HTTPException(status_code=503, detail=str(exc))
    elif season in available_historical:
        all_teams = historical.load_season(season)
    else:
        raise HTTPException(
            status_code=404,
            detail=f"Season '{season}' not found. Available: {available_historical}",
        )
    
    participants = _build_participants(rosters, all_teams)
    return StandingsResponse(participants=participants, fetched_at=fetched_at)



@router.post("/api/standings/refresh", response_model=StandingsResponse)
def refresh_standings():
    """Hit the NBA API, write results to Supabase, return fresh standings."""
    rosters = roster_store.load()
    if not rosters:
        return StandingsResponse(participants=[], fetched_at=None)
    try:
        all_teams = fetch_and_store_live_standings()  # hits NBA API + saves to Supabase
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc))
    participants = _build_participants(rosters, all_teams)
    _, fetched_at = standings_store.get_cached_standings()
    return StandingsResponse(participants=participants, fetched_at=fetched_at)


@router.get("/api/seasons")
def get_seasons():
    return {
        "current": CURRENT_SEASON,
        "historical": historical.list_seasons(),
    }


@router.get("/api/health")
def health():
    return {"status": "ok"}
