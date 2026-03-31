"""
Fetch end-of-season standings and save them as a historical snapshot.

Usage:
    python scripts/fetch_season_final.py --season 2024-25

Output:
    backend/data/historical/2024-25.json

Run this script at the end of each NBA season, then commit the output file.
"""

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from curl_cffi import requests as cffi_requests

NBA_STANDINGS_URL = "https://stats.nba.com/stats/leaguestandingsv3"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Referer": "https://www.nba.com/",
    "Origin": "https://www.nba.com",
    "x-nba-stats-origin": "stats",
    "x-nba-stats-token": "true",
    "Accept": "application/json",
}


def fetch(season: str) -> list[dict]:
    print(f"Fetching standings for season {season}...")
    response = cffi_requests.get(
        NBA_STANDINGS_URL,
        params={"LeagueID": "00", "Season": season, "SeasonType": "Regular Season"},
        headers=HEADERS,
        impersonate="chrome",
        timeout=30,
    )
    response.raise_for_status()

    payload = response.json()
    result_set = payload["resultSets"][0]
    col = {name: idx for idx, name in enumerate(result_set["headers"])}

    teams = []
    for row in result_set["rowSet"]:
        teams.append({
            "team_id": int(row[col["TeamID"]]),
            "name": row[col["TeamName"]],
            "abbreviation": row[col["TeamAbbreviation"]],
            "wins": int(row[col["WINS"]]),
            "losses": int(row[col["LOSSES"]]),
            "home_record": row[col["HOME"]] or "0-0",
            "away_record": row[col["ROAD"]] or "0-0",
            "last_10": row[col["L10"]] or "0-0",
            "conf_rank": int(row[col["PlayoffRank"]]),
            "conference": row[col["Conference"]],
        })

    return teams


def main():
    parser = argparse.ArgumentParser(description="Snapshot NBA season standings")
    parser.add_argument("--season", required=True, help="Season string e.g. 2024-25")
    args = parser.parse_args()

    season = args.season
    teams = fetch(season)

    out_dir = Path(__file__).parent.parent / "backend" / "data" / "historical"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{season}.json"

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump({"season": season, "generated_at": datetime.now(timezone.utc).isoformat(), "teams": teams}, f, indent=2)

    print(f"Saved {len(teams)} teams to {out_path}")
    print(f"Next step: git add {out_path} && git commit -m 'Add {season} final standings'")


if __name__ == "__main__":
    main()
