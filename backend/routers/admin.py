from fastapi import APIRouter, Depends
from backend.auth import require_api_key
from backend.models import RosterPayload
from backend.services import roster_store

router = APIRouter()


@router.post("/api/admin/rosters", dependencies=[Depends(require_api_key)])
def update_rosters(payload: RosterPayload):
    roster_store.save(payload.rosters)
    total_teams = sum(len(v) for v in payload.rosters.values())
    return {
        "saved": True,
        "participant_count": len(payload.rosters),
        "total_teams": total_teams,
    }
