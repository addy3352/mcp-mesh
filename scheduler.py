from apscheduler.schedulers.asyncio import AsyncIOScheduler
from garmin_sync import sync_garmin
from nutrition_sync import sync_nutrition

scheduler = AsyncIOScheduler()

def start_scheduler():
    scheduler.add_job(sync_garmin, "cron", hour=8)
    scheduler.add_job(sync_garmin, "cron", hour=23)
    scheduler.add_job(sync_nutrition, "cron", hour=23, minute=30)
    scheduler.start()
