from datetime import date
import asyncio
# REMOVED: from .db import init_db # init_db is only needed in server.py startup
from db import daily_summary as get_daily_summary # Use functions from local db.py
from notify import notify

# Implement this to read daily calories from your ChatGPT "Nutrition and Calories breakdown"
# For MVP, return the latest value already captured by your nutrition MCP,
# or set a manual number while you wire the extractor.
def fetch_daily_calories_from_source(d: date) -> int:
    # TODO: replace with your extraction logic
    # For now, let's assume a default or fetch from an external source (e.g., a file/API)
    return 2000

# Helper function to perform the database write using aiosqlite from local db.py
async def _insert_calories_daily(d: date, calories: int):
    # This must use aiosqlite/async DB logic
    from db import DB_PATH
    import aiosqlite
    
    # We must establish a connection here to use aiosqlite for this non-CRUD logic.
    async with aiosqlite.connect(DB_PATH) as db_conn:
        await db_conn.execute("""
        INSERT OR REPLACE INTO calories_daily(date, calories, source)
        VALUES (?, ?, 'nutrition-mcp')
        """, (d.isoformat(), calories))
        await db_conn.commit()


def sync_nutrition_daily(target: date | None = None):
    d = target or date.today()
    calories = fetch_daily_calories_from_source(d)
    
    # Run the async database write operation synchronously
    # This pattern is necessary if the calling code (router/scheduler) is synchronous
    try:
        asyncio.run(_insert_calories_daily(d, calories))
    except Exception as e:
        # Log the error if the DB operation fails
        print(f"ERROR during calorie sync on {d.isoformat()}: {e}")
        # Optionally notify of failure: notify("❌ Nutrition Sync Failed", f"Date: {d.isoformat()}. Error: {e}", etype="nutrition_sync_error")
        return

    # Fetch summary for notification payload (using local async function)
    # The get_daily_summary function needs to be run async
    summary = asyncio.run(get_daily_summary(d.isoformat()))
    
    # Send notification
    notify("nutrition.txt", {
        "calories": summary.get('calories'),
        "protein_status": f"{summary.get('protein', 0.0)} g logged", # Placeholder macro status
        "water_status": "Target on track" # Placeholder water status
    }, etype="nutrition_sync")
