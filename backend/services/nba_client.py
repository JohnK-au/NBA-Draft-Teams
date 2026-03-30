"""
Wraps the nba_api LeagueStandingsV3 endpoint.

One bulk call fetches all 30 teams. Results are cached for 5 minutes so
Render's shared CPU isn't hammered on every page load.
"""

import logging
from nba_api.stats.endpoints import leaguestandingsv3
from backend.cache import standings_cache
from backend.models import TeamStats

logger = logging.getLogger(__name__)

CACHE_KEY = "live_standings"


def _fetch_from_nba_api() -> list[TeamStats]:
    """Call the unofficial NBA stats API and return parsed TeamStats."""
    result = leaguestandingsv3.LeagueStandingsV3(timeout=30)
    rows = result.standings.get_dict()
    headers = rows["headers"]
    data = rows["data"]

    col = {name: idx for idx, name in enumerate(headers)}

    teams: list[TeamStats] = []
    for row in data:
        wins = int(row[col["WINS"]])
        losses = int(row[col["LOSSES"]])

        # HOME and ROAD come back as "W-L" strings e.g. "20-10"
        home_record = row[col["HOME"]] or "0-0"
        away_record = row[col["ROAD"]] or "0-0"
        last_10 = row[col["L10"]] or "0-0"

        teams.append(
            TeamStats(
                team_id=int(row[col["TeamID"]]),
                name=row[col["TeamName"]],
                abbreviation=row[col["TeamAbbreviation"]],
                wins=wins,
                losses=losses,
                home_record=home_record,
                away_record=away_record,
                last_10=last_10,
                conf_rank=int(row[col["PlayoffRank"]]),
                conference=row[col["Conference"]],
            )
        )

    return teams


def get_live_standings() -> list[TeamStats]:
    """
    Return all 30 team standings, using the cache when possible.
    On API failure, returns the last cached value if one exists.
    Raises RuntimeError if there is no cached value and the API call fails.
    """
    cached = standings_cache.get(CACHE_KEY)
    if cached is not None:
        return cached

    try:
        teams = _fetch_from_nba_api()
        standings_cache.set(CACHE_KEY, teams)
        return teams
    except Exception as exc:
        # Try to return stale data rather than hard-failing
        stale = standings_cache.get(CACHE_KEY)
        if stale is not None:
            logger.warning("NBA API call failed, serving stale cache: %s", exc)
            return stale
        raise RuntimeError(f"NBA API unavailable and no cached data: {exc}") from exc
