
from fastapi import APIRouter, Depends
from fastapi.concurrency import run_in_threadpool # CRITICAL: Import for synchronous code
from models import MealEntry, DailySummaryRequest, MealsQuery
from nutrition_db  import insert_meal, daily_summary, list_meals
from auth import require_api_key
from nutrition_sync import sync_nutrition_daily # Import the sync function
from datetime import date


router = APIRouter(dependencies=[Depends(require_api_key)])

# ADDED: Endpoint for nutrition.sync tool
@router.post("/nutrition.sync")
async def sync_daily_data(date: str | None = None):
    # CRITICAL FIX: Run synchronous sync_nutrition_daily in a threadpool
    target_date = date if date else None
    await run_in_threadpool(sync_nutrition_daily, target=target_date)
    return {"status": "ok", "synced_date": target_date or date.today().isoformat()}

@router.post("/nutrition.write_meal")
async def write_meal(entry: MealEntry):
    await insert_meal(entry.dict())
    return {"status":"ok","logged": entry}

@router.post("/nutrition.get_daily_summary")
async def get_daily_summary(body: DailySummaryRequest):
    return await daily_summary(body.date)

@router.post("/nutrition.list_meals")
async def get_meals(body: MealsQuery):
    items = await list_meals(date=body.date, start_date=body.start_date, end_date=body.end_date)
    return {"items": items}
