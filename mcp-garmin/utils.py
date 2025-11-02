
import os
from garminconnect import Garmin
from fastapi.concurrency import run_in_threadpool

class GarminClient:
    def __init__(self):
        email = os.getenv("GARMIN_EMAIL")
        pwd   = os.getenv("GARMIN_PASSWORD")
        if not email or not pwd:
            raise Exception("GARMIN_EMAIL/GARMIN_PASSWORD not set")
        self.client = Garmin(email, pwd)

    async def login(self):
        await run_in_threadpool(self.client.login)

    async def get_stats(self, date):
        return await run_in_threadpool(self.client.get_stats, date)

    async def get_user_summary(self, date):
        return await run_in_threadpool(self.client.get_user_summary, date)

    async def get_stats_and_body(self, date):
        return await run_in_threadpool(self.client.get_stats_and_body, date)

    async def get_steps_data(self, date):
        return await run_in_threadpool(self.client.get_steps_data, date)

    async def get_heart_rates(self, date):
        return await run_in_threadpool(self.client.get_heart_rates, date)

    async def get_resting_heart_rate(self, date):
        return await run_in_threadpool(self.client.get_rhr_day, date)

    async def get_sleep_data(self, date):
        return await run_in_threadpool(self.client.get_sleep_data, date)

    async def get_all_day_stress(self, date):
        return await run_in_threadpool(self.client.get_stress_data, date)

    async def get_training_readiness(self, date):
        return await run_in_threadpool(self.client.get_training_readiness, date)

    async def get_training_status(self, date):
        return await run_in_threadpool(self.client.get_training_status, date)

    async def get_respiration_data(self, date):
        return await run_in_threadpool(self.client.get_respiration_data, date)

    async def get_spo2_data(self, date):
        return await run_in_threadpool(self.client.get_spo2_data, date)

    async def get_max_metrics(self, date):
        return await run_in_threadpool(self.client.get_max_metrics, date)

    async def get_hrv_data(self, date):
        return await run_in_threadpool(self.client.get_hrv_data, date)

    async def get_fitnessage_data(self, date):
        return await run_in_threadpool(self.client.get_fitnessage_data, date)

    async def get_stress_data(self, date):
        return await run_in_threadpool(self.client.get_stress_data, date)

    async def get_lactate_threshold(self, date):
        return await run_in_threadpool(self.client.get_lactate_threshold, date)

    async def get_intensity_minutes_data(self, date):
        return await run_in_threadpool(self.client.get_intensity_minutes, date)

    async def get_activities_range(self, start_date, end_date):
        return await run_in_threadpool(self.client.get_activities_by_date, start_date, end_date)
