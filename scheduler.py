import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from mcp_client import call_tool

async def sync_garmin():
    await call_tool("mcp-garmin.sync", {})

async def sync_nutrition():
    await call_tool("mcp-nutrition.sync", {})

def start_scheduler():
    scheduler = AsyncIOScheduler(timezone="Asia/Dubai")
    scheduler.add_job(lambda: asyncio.create_task(sync_garmin()), 'cron', hour=8, minute=0)
    scheduler.add_job(lambda: asyncio.create_task(sync_garmin()), 'cron', hour=23, minute=0)
    scheduler.add_job(lambda: asyncio.create_task(sync_nutrition()), 'cron', hour=0, minute=5)
    scheduler.start()

if __name__ == "__main__":
    import uvloop
    uvloop.install()
    start_scheduler()
    asyncio.get_event_loop().run_forever()
