
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from datetime import date, timedelta
from utils import GarminClient

router = APIRouter()

async def get_client():
    client = GarminClient()
    await client.login()
    return client

class DateBody(BaseModel):
    date: date

class DateRange(BaseModel):
    start_date: date | None = None
    end_date: date | None = None

@router.post("/garmin.get_stats")
async def get_stats(body: DateBody, client: GarminClient = Depends(get_client)):
    return await client.get_stats(body.date.isoformat())

@router.post("/garmin.get_user_summary")
async def get_user_summary(body: DateBody, client: GarminClient = Depends(get_client)):
    return await client.get_user_summary(body.date.isoformat())

@router.post("/garmin.get_stats_and_body")
async def get_stats_and_body(body: DateBody, client: GarminClient = Depends(get_client)):
    return await client.get_stats_and_body(body.date.isoformat())

@router.post("/garmin.get_steps_data")
async def get_steps_data(body: DateBody, client: GarminClient = Depends(get_client)):
    return await client.get_steps_data(body.date.isoformat())

@router.post("/garmin.get_heart_rates")
async def get_heart_rates(body: DateBody, client: GarminClient = Depends(get_client)):
    return await client.get_heart_rates(body.date.isoformat())

@router.post("/garmin.get_resting_heart_rate")
async def get_resting_hr(body: DateBody, client: GarminClient = Depends(get_client)):
    return await client.get_resting_heart_rate(body.date.isoformat())

@router.post("/garmin.get_sleep_data")
async def get_sleep_data(body: DateBody, client: GarminClient = Depends(get_client)):
    return await client.get_sleep_data(body.date.isoformat())

@router.post("/garmin.get_all_day_stress")
async def get_all_day_stress(body: DateBody, client: GarminClient = Depends(get_client)):
    return await client.get_all_day_stress(body.date.isoformat())

@router.post("/garmin.get_training_readiness")
async def get_training_readiness(body: DateBody, client: GarminClient = Depends(get_client)):
    return await client.get_training_readiness(body.date.isoformat())

@router.post("/garmin.get_training_status")
async def get_training_status(body: DateBody, client: GarminClient = Depends(get_client)):
    return await client.get_training_status(body.date.isoformat())

@router.post("/garmin.get_respiration_data")
async def get_respiration_data(body: DateBody, client: GarminClient = Depends(get_client)):
    return await client.get_respiration_data(body.date.isoformat())

@router.post("/garmin.get_spo2_data")
async def get_spo2_data(body: DateBody, client: GarminClient = Depends(get_client)):
    return await client.get_spo2_data(body.date.isoformat())

@router.post("/garmin.get_max_metrics")
async def get_max_metrics(body: DateBody, client: GarminClient = Depends(get_client)):
    return await client.get_max_metrics(body.date.isoformat())

@router.post("/garmin.get_hrv_data")
async def get_hrv_data(body: DateBody, client: GarminClient = Depends(get_client)):
    return await client.get_hrv_data(body.date.isoformat())

@router.post("/garmin.get_fitnessage_data")
async def get_fitnessage_data(body: DateBody, client: GarminClient = Depends(get_client)):
    return await client.get_fitnessage_data(body.date.isoformat())

@router.post("/garmin.get_stress_data")
async def get_stress_data(body: DateBody, client: GarminClient = Depends(get_client)):
    return await client.get_stress_data(body.date.isoformat())

@router.post("/garmin.get_lactate_threshold")
async def get_lactate_threshold(body: DateBody, client: GarminClient = Depends(get_client)):
    return await client.get_lactate_threshold(body.date.isoformat())

@router.post("/garmin.get_intensity_minutes_data")
async def get_intensity_minutes(body: DateBody, client: GarminClient = Depends(get_client)):
    return await client.get_intensity_minutes_data(body.date.isoformat())

@router.post("/garmin.get_activities_range")
async def get_activities_range(body: DateRange | None = None, client: GarminClient = Depends(get_client)):
    if body is None or not body.start_date or not body.end_date:
        end = date.today()
        start = end - timedelta(days=7)
    else:
        start = body.start_date
        end = body.end_date
    return await client.get_activities_range(start.isoformat(), end.isoformat())
