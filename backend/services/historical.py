"""
Loads end-of-season snapshot files from backend/data/historical/.

Each file is named YYYY-YY.json and contains:
{
  "season": "2023-24",
  "generated_at": "2024-09-01T00:00:00Z",
  "teams": [ <TeamStats objects> ]
}
"""

import json
from pathlib import Path
from backend.models import TeamStats

HISTORICAL_DIR = Path(__file__).parent.parent / "data" / "historical"


def list_seasons() -> list[str]:
    """Return sorted list of available historical season identifiers, e.g. ['2022-23', '2023-24']."""
    if not HISTORICAL_DIR.exists():
        return []
    seasons = [
        p.stem for p in sorted(HISTORICAL_DIR.glob("*.json"))
    ]
    return seasons


def load_season(season: str) -> list[TeamStats]:
    """
    Load and return all TeamStats for the given historical season string (e.g. '2023-24').
    Raises FileNotFoundError if the season file doesn't exist.
    """
    path = HISTORICAL_DIR / f"{season}.json"
    if not path.exists():
        raise FileNotFoundError(f"No historical data found for season '{season}'")
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    return [TeamStats(**t) for t in data["teams"]]
