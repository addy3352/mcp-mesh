from datetime import date
from db import db
from notify import notify

# Implement this to read daily calories from your ChatGPT "Nutrition and Calories breakdown"
# For MVP, return the latest value already captured by your nutrition MCP,
# or set a manual number while you wire the extractor.
def fetch_daily_calories_from_source(d: date) -> int:
    # TODO: replace with your extraction
    return 2000

def sync_nutrition_daily(target: date | None = None):
    d = target or date.today()
    calories = fetch_daily_calories_from_source(d)
    with db() as conn:
        conn.execute("""
        INSERT OR REPLACE INTO calories_daily(date, calories, source)
        VALUES (?, ?, 'nutrition-mcp')
        """, (d.isoformat(), calories))
    notify("🍽️ Nutrition synced", f"{d.isoformat()}: {calories} kcal", {"date": d.isoformat(), "calories": calories}, etype="nutrition_sync")
