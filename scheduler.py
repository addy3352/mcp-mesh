# scheduler.py (Simplified and Recommended)
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from mcp_client import call_tool # Used for internal tool calls

# Use Asia/Dubai timezone for cron jobs
scheduler = AsyncIOScheduler(timezone="Asia/Dubai")

async def sync_garmin():
    # Call the dedicated sync tool in the mcp-garmin service via mesh-gateway
    print("Triggering garmin.sync...")
    await call_tool("garmin.sync", role="system-scheduler")

async def sync_nutrition():
    # Call the dedicated sync tool in the mcp-nutrition service via mesh-gateway
    print("Triggering nutrition.sync...")
    await call_tool("nutrition.sync", role="system-scheduler")

# This function is async so it can be awaited in the lifespan hook of server.py
async def start_scheduler():
    # Morning sync (08:00)
    # The AsyncIOScheduler can execute coroutines directly.
    scheduler.add_job(sync_garmin, 'cron', hour=8, minute=0)
    # Evening sync (23:00) for final daily stats/sleep
    scheduler.add_job(sync_garmin, 'cron', hour=23, minute=0)
    # Post-midnight nutrition sync (00:05) for final daily totals
    scheduler.add_job(sync_nutrition, 'cron', hour=0, minute=5)

    print("Starting APScheduler...")
    scheduler.start()

    # CRITICAL FIX: Return the scheduler instance for shutdown cleanup in server.py's lifespan
    return scheduler
