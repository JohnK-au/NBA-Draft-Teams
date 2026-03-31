from fastapi import APIRouter, HTTPException, Query
from backend.models import ParticipantStats, AggregateRecord, TeamStats
from backend.services import roster_store, historical
from backend.services.nba_client import get_live_standings

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


@router.get("/api/participants", response_model=list[ParticipantStats])
def get_participants(
    season: str = Query(default=CURRENT_SEASON, description="Season string e.g. '2024-25'"),
):
    rosters = roster_store.load()
    if not rosters:
        return []

    available_historical = historical.list_seasons()

    if season == CURRENT_SEASON:
        try:
            all_teams = get_live_standings()
        except RuntimeError as exc:
            raise HTTPException(status_code=503, detail=str(exc))
    elif season in available_historical:
        all_teams = historical.load_season(season)
    else:
        raise HTTPException(
            status_code=404,
            detail=f"Season '{season}' not found. Available: {available_historical}",
        )

    return _build_participants(rosters, all_teams)


@router.get("/api/seasons")
def get_seasons():
    return {
        "current": CURRENT_SEASON,
        "historical": historical.list_seasons(),
    }


@router.get("/api/health")
def health():
    return {"status": "ok"}
