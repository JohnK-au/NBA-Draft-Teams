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
from backend.services import standings_store


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

# The NBA API has no abbreviation field — this map is stable (team IDs never change)
TEAM_ABBREVIATIONS: dict[int, str] = {
    1610612737: "ATL", 1610612738: "BOS", 1610612739: "CLE", 1610612740: "NOP",
    1610612741: "CHI", 1610612742: "DAL", 1610612743: "DEN", 1610612744: "GSW",
    1610612745: "HOU", 1610612746: "LAC", 1610612747: "LAL", 1610612748: "MIA",
    1610612749: "MIL", 1610612750: "MIN", 1610612751: "BKN", 1610612752: "NYK",
    1610612753: "ORL", 1610612754: "IND", 1610612755: "PHI", 1610612756: "PHX",
    1610612757: "POR", 1610612758: "SAC", 1610612759: "SAS", 1610612760: "OKC",
    1610612761: "TOR", 1610612762: "UTA", 1610612763: "MEM", 1610612764: "WAS",
    1610612765: "DET", 1610612766: "CHA",
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
                abbreviation=TEAM_ABBREVIATIONS.get(int(row[col["TeamID"]]), "???"),
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

    teams, _ = standings_store.get_cached_standings()
    if teams:
        return teams
    # Cache is empty, fetch from NBA API and populate
    return fetch_and_store_live_standings()


def fetch_and_store_live_standings() -> list[TeamStats]:

    teams = _fetch_from_nba_api()
    standings_store.save_standings(teams)
    return teams

