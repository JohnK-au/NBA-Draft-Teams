"""
Reads and writes rosters from Supabase (participants + rosters tables).
Returns a dict mapping participant name to list of team_ids:
{
  "Alice": [1610612747, 1610612738],
  "Bob":   [1610612744, 1610612760]
}
"""

from backend.services.supabase_client import db

def load() -> dict[str, list[int]]:
    # Join rosters -> participants to get {name: [team_ids]}
    result = db.table("rosters").select("team_id, participants(name)").execute()

    rosters: dict[str, list[int]] = {}
    for row in result.data:
        name = row["participants"]["name"]
        rosters.setdefault(name, []).append(row["team_id"])

    return rosters

def save(rosters: dict[str, list[int]]) -> None:
   for name, team_ids in rosters.items():
        # Upsert participant name to get participant_id
        participant_result = db.table("participants").upsert({"name": name}, on_conflict="name").execute()
        participant_id = participant_result.data[0]["id"]

        # Delete existing roster rows for this participant
        db.table("rosters").delete().eq("participant_id", participant_id).execute()

        # Insert new roster rows
        new_rows = [{"participant_id": participant_id, "team_id": team_id} for team_id in team_ids]
        if new_rows:
            db.table("rosters").insert(new_rows).execute()
