"""
Fetches NBA standings directly from the unofficial NBA stats API.

Uses curl_cffi to impersonate a browser TLS fingerprint, which is required
because stats.nba.com blocks Python's default TLS client hello.
Results are cached for 5 minutes to avoid hammering the API.
"""

import logging
from curl_cffi import requests as cffi_requests
from backend.cache import standings_cache
from backend.models import TeamStats

logger = logging.getLogger(__name__)

CACHE_KEY = "live_standings"

NBA_STANDINGS_URL = "https://stats.nba.com/stats/leaguestandingsv3"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Referer": "https://www.nba.com/",
    "Origin": "https://www.nba.com",
    "x-nba-stats-origin": "stats",
    "x-nba-stats-token": "true",
    "Accept": "application/json",
}

PARAMS = {
    "LeagueID": "00",
    "Season": "2025-26",
    "SeasonType": "Regular Season",
}


def _fetch_from_nba_api() -> list[TeamStats]:
    response = cffi_requests.get(
        NBA_STANDINGS_URL,
        params=PARAMS,
        headers=HEADERS,
        impersonate="chrome",
        timeout=30,
    )
    response.raise_for_status()

    payload = response.json()
    result_set = payload["resultSets"][0]
    headers = result_set["headers"]
    data = result_set["rowSet"]

    col = {name: idx for idx, name in enumerate(headers)}

    teams: list[TeamStats] = []
    for row in data:
        teams.append(
            TeamStats(
                team_id=int(row[col["TeamID"]]),
                name=row[col["TeamName"]],
                abbreviation=row[col["TeamAbbreviation"]],
                wins=int(row[col["WINS"]]),
                losses=int(row[col["LOSSES"]]),
                home_record=row[col["HOME"]] or "0-0",
                away_record=row[col["ROAD"]] or "0-0",
                last_10=row[col["L10"]] or "0-0",
                conf_rank=int(row[col["PlayoffRank"]]),
                conference=row[col["Conference"]],
            )
        )

    return teams


def get_live_standings() -> list[TeamStats]:
    cached = standings_cache.get(CACHE_KEY)
    if cached is not None:
        return cached

    try:
        teams = _fetch_from_nba_api()
        standings_cache.set(CACHE_KEY, teams)
        return teams
    except Exception as exc:
        stale = standings_cache.get(CACHE_KEY)
        if stale is not None:
            logger.warning("NBA API call failed, serving stale cache: %s", exc)
            return stale
        raise RuntimeError(f"NBA API unavailable and no cached data: {exc}") from exc
