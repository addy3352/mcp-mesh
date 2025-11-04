from apscheduler.schedulers.asyncio import AsyncIOScheduler
import asyncio
from mcp_client import call_tool

async def sync_garmin():
    await call_tool("garmin.sync")

async def sync_nutrition():
    await call_tool("nutrition.sync")

scheduler = AsyncIOScheduler(timezone="Asia/Dubai")

def start_scheduler():
    scheduler.add_job(lambda: asyncio.create_task(sync_garmin()), 'cron', hour=8, minute=0)
    scheduler.add_job(lambda: asyncio.create_task(sync_garmin()), 'cron', hour=23, minute=0)
    scheduler.add_job(lambda: asyncio.create_task(sync_nutrition()), 'cron', hour=0, minute=5)
    print("Starting APScheduler...")
    scheduler.start()
