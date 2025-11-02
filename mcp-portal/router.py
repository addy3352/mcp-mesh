
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import requests, os

router = APIRouter()

PORTAL_URL   = os.getenv("PORTAL_API_URL")
PORTAL_TOKEN = os.getenv("PORTAL_API_KEY")

class HealthPanelEntry(BaseModel):
    date: str
    steps: int | None = None
    calories: float | None = None
    rhr: float | None = None
    hrv: float | None = None
    sleep_hours: float | None = None
    stress_score: float | None = None
    recommendation: str

@router.post("/portal.update_health_panel")
def update_portal(entry: HealthPanelEntry):
    if not PORTAL_URL:
        raise HTTPException(status_code=500, detail="PORTAL_API_URL not set")
    headers = {"Authorization": f"Bearer {PORTAL_TOKEN}", "Content-Type": "application/json"}
    try:
        r = requests.post(f"{PORTAL_URL}/api/health/update", json=entry.dict(), headers=headers, timeout=10)
        r.raise_for_status()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Portal API error: {str(e)}")
    return {"ok": True, "synced": entry.date}
