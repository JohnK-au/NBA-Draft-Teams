from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from backend.routers import participants, admin

app = FastAPI(title="NBA Draft Tracker", docs_url="/docs")

app.include_router(participants.router)
app.include_router(admin.router)

# Serve the built React frontend at / in production.
# In dev, Vite runs separately and proxies /api/* to this server.
_dist = Path(__file__).parent.parent / "frontend" / "dist"
if _dist.exists():
    app.mount("/", StaticFiles(directory=str(_dist), html=True), name="static")
