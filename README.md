# NBA Team Draft Tracker

A lightweight web app for tracking a friend-group NBA team draft across a full season. Each participant drafts a set of NBA teams at the start of the season. This app shows live standings, records, and comparisons so you can see who's winning the draft.

## Features

- Live W-L record, home/away split, last-10, and conference standing for every drafted team
- Aggregate combined record per participant, sorted by win percentage
- Historical seasons stored as static JSON files — no database required
- Admin endpoint to update rosters after the draft (protected by API key)
- Fully free and open-source: Python + FastAPI backend, React + Vite frontend, deployed on Render.com free tier

## Project Structure

```
nba_team_draft/
├── backend/           # FastAPI app + NBA data fetching
│   ├── data/
│   │   ├── rosters.json          # Who drafted which teams
│   │   └── historical/           # End-of-season snapshots (committed to repo)
│   └── ...
├── frontend/          # React + Vite (TypeScript) app
└── scripts/           # Utility scripts (season snapshot generator)
```

## Local Development

### Prerequisites
- Python 3.11+
- Node.js 18+

### Backend

```bash
cd backend
pip install -r requirements.txt

# Start the API server (reload on file changes)
ADMIN_API_KEY=dev uvicorn main:app --reload --port 8000
```

API will be available at `http://localhost:8000`.
Interactive docs: `http://localhost:8000/docs`

### Frontend

```bash
cd frontend
npm install
npm run dev
```

App will be available at `http://localhost:5173`. The Vite dev server proxies all `/api/*` requests to the backend at port 8000.

---

## Configuring Rosters

After running your draft, update `backend/data/rosters.json` directly (recommended) or POST to the admin endpoint:

```bash
curl -X POST http://localhost:8000/api/admin/rosters \
  -H "X-API-Key: dev" \
  -H "Content-Type: application/json" \
  -d '{
    "rosters": {
      "Alice": [1610612747, 1610612738],
      "Bob":   [1610612744, 1610612760],
      "Carol": [1610612748, 1610612749]
    }
  }'
```

To find NBA team IDs, run:

```bash
cd backend
python -c "from nba_api.stats.static import teams; import json; print(json.dumps(teams.get_teams(), indent=2))"
```

> **Note:** On Render free tier, filesystem writes are lost on redeploy. The recommended workflow is to edit `backend/data/rosters.json` directly and commit it to git — Render will redeploy automatically.

---

## Adding Historical Season Data

At the end of each season, generate a snapshot and commit it:

```bash
python scripts/fetch_season_final.py --season 2024-25
# Writes to backend/data/historical/2024-25.json
```

Then commit the file:

```bash
git add backend/data/historical/2024-25.json
git commit -m "Add 2024-25 final standings snapshot"
git push
```

The season will automatically appear in the season selector dropdown.

---

## Deployment (Render.com Free Tier)

1. Push this repo to GitHub (public or private).
2. Go to [render.com](https://render.com) → **New Web Service** → connect your GitHub repo.
3. Render will auto-detect `render.yaml`.
4. In the Render dashboard → **Environment** tab, add:
   - `ADMIN_API_KEY` = a secret string of your choice (never commit this)
5. Click **Deploy**. After a few minutes you'll have a public URL to share with friends.

**Cold start note:** Render free-tier services spin down after 15 minutes of inactivity. The first request after a period of inactivity takes ~30 seconds to respond. This is normal — the app shows a loading state while it wakes up.

---

## Tech Stack

| Layer | Tool | License |
|---|---|---|
| Backend framework | [FastAPI](https://fastapi.tiangolo.com/) | MIT |
| NBA data | [nba_api](https://github.com/swar/nba_api) | MIT |
| Frontend | [React](https://react.dev/) + [Vite](https://vitejs.dev/) | MIT |
| Hosting | [Render.com](https://render.com) free tier | — |
