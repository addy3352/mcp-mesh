
import os
from fastapi import Header, HTTPException

API_KEY = os.getenv("NUTRITION_API_KEY", "").strip()

async def require_api_key(x_api_key: str | None = Header(default=None)):
    if API_KEY and x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")
