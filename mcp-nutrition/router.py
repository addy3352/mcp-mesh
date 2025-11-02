
from fastapi import APIRouter, Depends
from models import MealEntry, DailySummaryRequest, MealsQuery
from db import insert_meal, daily_summary, list_meals
from auth import require_api_key

router = APIRouter(dependencies=[Depends(require_api_key)])

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
