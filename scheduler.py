# scheduler.py (Corrected)
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import asyncio
from mcp_client import call_tool # Used for internal tool calls

scheduler = AsyncIOScheduler(timezone="Asia/Dubai")

async def sync_garmin():
    # Tool call to mcp-garmin service via mesh-gateway
    await call_tool("garmin.sync", role="system-scheduler")

async def sync_nutrition():
    # Tool call to mcp-nutrition service via mesh-gateway
    await call_tool("nutrition.sync", role="system-scheduler")

# Make this function async so it can be awaited in the lifespan hook
async def start_scheduler():
    scheduler.add_job(lambda: asyncio.create_task(sync_garmin()), 'cron', hour=8, minute=0)
    scheduler.add_job(lambda: asyncio.create_task(sync_garmin()), 'cron', hour=23, minute=0)
    scheduler.add_job(lambda: asyncio.create_task(sync_nutrition()), 'cron', hour=0, minute=5)
    
    print("Starting APScheduler...")
    scheduler.start()
    
    # CRITICAL FIX: Return the scheduler instance for shutdown cleanup
    return scheduler