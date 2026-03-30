import os
from fastapi import Header, HTTPException


async def require_api_key(x_api_key: str = Header(...)) -> None:
    expected = os.environ.get("ADMIN_API_KEY", "")
    if not expected or x_api_key != expected:
        raise HTTPException(status_code=403, detail="Invalid or missing API key")
