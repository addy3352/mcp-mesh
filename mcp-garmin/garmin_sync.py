import os
from datetime import date
from fastapi.concurrency import run_in_threadpool
from garminconnect import Garmin
from db import db
from notify import notify

GARMIN_EMAIL = os.getenv("GARMIN_EMAIL")
GARMIN_PASSWORD = os.getenv("GARMIN_PASSWORD")
print("Gaeminn email {}and password to test {}".format(GARMIN_EMAIL,GARMIN_PASSWORD))   

async def _login() -> Garmin:
    g = Garmin(GARMIN_EMAIL, GARMIN_PASSWORD)
    try:
        await run_in_threadpool(g.login)
        print("Garmin login successful.")
        return g
    except Exception as e:
        print(f"Garmin login failed with exception: {e}")
        # It's possible the profile is not what's expected.
        # Let's try to see what garth object contains.
        if hasattr(g, 'garth') and hasattr(g.garth, '_profile'):
             print(f"Garth raw profile attribute: {g.garth._profile}")
        raise



async def sync_garmin_daily(target: date | None = None):
    d = target or date.today()
    g = await _login()
    # Pull daily summary by date
    summary = await run_in_threadpool(g.get_stats, d.isoformat())
    hr = await run_in_threadpool(g.get_heart_rates, d.isoformat())
    sleep = await run_in_threadpool(g.get_sleep_data, d.isoformat())
    tr_load = await run_in_threadpool(g.get_training_status, d.isoformat())
    vo2 = await run_in_threadpool(g.get_max_metrics, d.isoformat())

    # Map safely
    steps = summary.get("totalSteps") or 0
    calories = summary.get("totalCalories") or 0
    distance_km = round((summary.get("totalDistance") or 0) / 1000, 2)
    sleep_hours = round((sleep.get("sleepTimeSeconds") or 0) / 3600, 2)
    hrv_ms = (summary.get("hrvSummary", {}) or {}).get("lastNightAvg") or 0
    rhr_bpm = summary.get("restingHeartRate") or 0
    stress = summary.get("stressLevel") or 0
    training_load = (tr_load or {}).get("trainingLoad") or 0
    readiness = (summary.get("trainingReadinessScore") or 0)
    vo2max = (vo2 or {}).get("vo2Max") or 0

    with db() as conn:
        conn.execute("""
        INSERT OR REPLACE INTO garmin_daily
        (date, steps, calories, distance_km, sleep_hours, hrv_ms, rhr_bpm, stress, training_load, vo2max, readiness)
        VALUES (?,?,?,?,?,?,?,?,?,?,?)
        """, (d.isoformat(), steps, calories, distance_km, sleep_hours, hrv_ms, rhr_bpm, stress, training_load, vo2max, readiness))

    notify(
        template_name="manual_garmin_sync.txt",
        vars={
            "distance_km": distance_km,
            "rhr_bpm": rhr_bpm,
            "hrv_ms": hrv_ms,
            "sleep_hours": sleep_hours
        },
        etype="garmin_sync"
    )
