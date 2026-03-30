"""
Reads and writes backend/data/rosters.json.

Format:
{
  "Alice": [1610612747, 1610612738],
  "Bob":   [1610612744, 1610612760]
}
"""

import json
import os
import tempfile
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"
ROSTERS_PATH = DATA_DIR / "rosters.json"


def load() -> dict[str, list[int]]:
    """Return the current rosters dict. Returns empty dict if file missing."""
    if not ROSTERS_PATH.exists():
        return {}
    with open(ROSTERS_PATH, encoding="utf-8") as f:
        return json.load(f)


def save(rosters: dict[str, list[int]]) -> None:
    """
    Atomically replace rosters.json with new content.
    Writes to a temp file first to avoid partial writes corrupting reads.
    """
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    fd, tmp_path = tempfile.mkstemp(dir=DATA_DIR, suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(rosters, f, indent=2)
        os.replace(tmp_path, ROSTERS_PATH)
    except Exception:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise
