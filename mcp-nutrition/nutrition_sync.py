# mcp-nutrition/nutrition_sync.py

from datetime import date
import asyncio
from nutrition_db import daily_summary as get_daily_summary, insert_meal as log_daily_summary 
from notify import notify

# Implement this to read daily nutrition data from your source (e.g., ChatGPT output).
# It should return a dictionary with all required fields (calories, protein, carbs, fat).
def fetch_daily_nutrition_summary(d: date) -> dict:
    # TODO: Replace with your actual extraction logic from raw data.
    # For MVP, returning mock data that includes macros.
    return {
        "calories": 2000,
        "protein": 150,
        "carbs": 250,
        "fat": 60,
        "source": "sync_agent"
    }

async def sync_nutrition_daily(target: date | None = None):
    d = target or date.today()
    
    # 1. Fetch comprehensive nutrition data (including macros)
    nutrition_data = fetch_daily_nutrition_summary(d)
    
    # 2. Log the comprehensive daily summary. 
    # This uses the assumed function in nutrition_db.py which must handle all macro columns.
    await log_daily_summary({
        "date": d.isoformat(),
        "meal": "daily_summary",
        "description": nutrition_data.get("source", "sync_agent"),
        "calories": nutrition_data.get("calories", 0),
        "protein": nutrition_data.get("protein", 0),
        "carbs": nutrition_data.get("carbs", 0),
        "fat": nutrition_data.get("fat", 0),
    })

    # 3. Fetch the currently running total (from meals + synched data) for the notification context
    summary = await get_daily_summary(d.isoformat())

    # 4. Send notification
    notify("nutrition.txt",
        {
            "calories": int(summary["calories"]),
            "protein_status": f"{summary['protein']}g (Target TBD)",
            "water_status": "2.5L (Default)"
        },
        etype="nutrition_sync"
    )
    # The return value for the FastAPI endpoint
    return {"date": d.isoformat(), "summary_logged": nutrition_data}