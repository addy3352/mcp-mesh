# mcp-agent-health/agent_scheduler.py
import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from mcp_client import call_tool  # small wrapper you will create

async def sync_garmin():
    await call_tool("garmin.sync")

async def sync_nutrition():
    await call_tool("nutrition.sync")

def start_scheduler():
    scheduler = AsyncIOScheduler(timezone="Asia/Dubai")
    scheduler.add_job(lambda: asyncio.create_task(sync_garmin()), 'cron', hour=8, minute=0)
    scheduler.add_job(lambda: asyncio.create_task(sync_garmin()), 'cron', hour=23, minute=0)
    scheduler.add_job(lambda: asyncio.create_task(sync_nutrition()), 'cron', hour=0, minute=5)
    scheduler.start()
