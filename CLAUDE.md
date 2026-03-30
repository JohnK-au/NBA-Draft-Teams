# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

### Backend
```bash
# From repo root — activate venv first if using one
cd backend
pip install -r requirements.txt
ADMIN_API_KEY=dev uvicorn backend.main:app --reload --port 8000
```
Run from the **repo root**, not from inside `backend/`, because imports use the `backend.*` package path (e.g. `from backend.models import ...`).

### Frontend
```bash
cd frontend
npm install
npm run dev      # Vite dev server on :5173, proxies /api/* → localhost:8000
npm run build    # tsc -b && vite build → frontend/dist/
npm run lint
```

### Season snapshot (end of season)
```bash
python scripts/fetch_season_final.py --season 2024-25
# writes backend/data/historical/2024-25.json — commit the result
```

## Architecture

Single Render.com web service: FastAPI serves the API at `/api/*` and, in production, mounts the built React app (`frontend/dist/`) at `/` via `StaticFiles(html=True)`. No separate frontend host; no CORS needed.

**Data flow for a page load:**
1. React `Dashboard` → `useParticipants(season)` hook → `GET /api/participants?season=...`
2. FastAPI reads `backend/data/rosters.json` (participant → list of NBA `team_id`s)
3. For the current season: `nba_client.py` calls `LeagueStandingsV3` (one bulk call for all 30 teams), cached 5 min in `cache.py` (`TTLCache`)
4. For historical seasons: `historical.py` reads `backend/data/historical/YYYY-YY.json`
5. Response assembled in `routers/participants.py` → sorted by aggregate win %

**No database.** All persistent state lives in two committed files:
- `backend/data/rosters.json` — who drafted which teams (keyed by NBA integer `team_id`)
- `backend/data/historical/*.json` — end-of-season snapshots

**Admin endpoint** (`POST /api/admin/rosters`) is protected by `X-API-Key` header checked against `ADMIN_API_KEY` env var. On Render free tier, filesystem writes don't survive redeploys — the canonical workflow is to edit `rosters.json` directly and commit/push.

**NBA `team_id` values** are stable integers from the unofficial NBA stats API. To look them up:
```bash
python -c "from nba_api.stats.static import teams; import json; print(json.dumps(teams.get_teams(), indent=2))"
```

## Key files
- `backend/routers/participants.py` — main business logic: merges rosters with live/historical standings
- `backend/services/nba_client.py` — `LeagueStandingsV3` field mapping; if NBA API changes column names, fix here
- `backend/main.py` — router registration + static file mount (conditional on `frontend/dist/` existing)
- `frontend/src/pages/Dashboard.tsx` — top-level page; owns season state
- `frontend/src/hooks/useParticipants.ts` — all data fetching
