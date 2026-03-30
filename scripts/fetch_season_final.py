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
import sys
from datetime import datetime, timezone
from pathlib import Path

# Allow running from the repo root
sys.path.insert(0, str(Path(__file__).parent.parent))

from nba_api.stats.endpoints import leaguestandingsv3


def fetch(season: str) -> list[dict]:
    print(f"Fetching standings for season {season}...")
    result = leaguestandingsv3.LeagueStandingsV3(season=season, timeout=30)
    rows = result.standings.get_dict()
    headers = rows["headers"]
    data = rows["data"]
    col = {name: idx for idx, name in enumerate(headers)}

    teams = []
    for row in data:
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

    payload = {
        "season": season,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "teams": teams,
    }

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)

    print(f"Saved {len(teams)} teams to {out_path}")
    print(f"Next step: git add {out_path} && git commit -m 'Add {season} final standings'")


if __name__ == "__main__":
    main()
