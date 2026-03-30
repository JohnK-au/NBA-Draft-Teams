import time
from typing import Any


class TTLCache:
    """Simple in-memory TTL cache. Not thread-safe but fine for a single-worker FastAPI process."""

    def __init__(self, ttl_seconds: int = 300):
        self._ttl = ttl_seconds
        self._store: dict[str, tuple[float, Any]] = {}

    def get(self, key: str) -> Any | None:
        entry = self._store.get(key)
        if entry is None:
            return None
        expires_at, value = entry
        if time.monotonic() > expires_at:
            del self._store[key]
            return None
        return value

    def set(self, key: str, value: Any) -> None:
        self._store[key] = (time.monotonic() + self._ttl, value)

    def clear(self) -> None:
        self._store.clear()


# Shared cache instance used by nba_client
standings_cache = TTLCache(ttl_seconds=300)
