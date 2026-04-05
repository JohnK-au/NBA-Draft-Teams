from datetime import datetime
from pydantic import BaseModel


class TeamStats(BaseModel):
    team_id: int
    name: str
    abbreviation: str
    wins: int
    losses: int
    home_record: str   # e.g. "20-10"
    away_record: str   # e.g. "12-14"
    last_10: str       # e.g. "6-4"
    conf_rank: int
    conference: str    # "East" or "West"


class AggregateRecord(BaseModel):
    wins: int
    losses: int
    win_pct: float


class ParticipantStats(BaseModel):
    name: str
    teams: list[TeamStats]
    aggregate: AggregateRecord


class RosterPayload(BaseModel):
    rosters: dict[str, list[int]]


class StandingsResponse(BaseModel):
    participants: list[ParticipantStats]
    fetched_at: datetime | None

class AllTimeEntry(BaseModel):
    participant_name: str
    total: AggregateRecord
    per_season: dict[str, AggregateRecord]