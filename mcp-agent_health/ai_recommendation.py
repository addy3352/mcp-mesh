from .mesh.db import db

def compute_recommendation():
    with db() as conn:
        # last 7 days aggregates
        hrv = [r["hrv_ms"] for r in conn.execute("SELECT hrv_ms FROM garmin_daily ORDER BY date DESC LIMIT 7")]
        rhr = [r["rhr_bpm"] for r in conn.execute("SELECT rhr_bpm FROM garmin_daily ORDER BY date DESC LIMIT 7")]
        sleep = [r["sleep_hours"] for r in conn.execute("SELECT sleep_hours FROM garmin_daily ORDER BY date DESC LIMIT 7")]
        cal  = [r["calories"] for r in conn.execute("SELECT calories FROM calories_daily ORDER BY date DESC LIMIT 7")]

        latest = conn.execute("SELECT * FROM garmin_daily ORDER BY date DESC LIMIT 1").fetchone()

    # simple heuristic for MVP (WHOOP + Strava tone); you can swap with LLM later
    rec_score = 80
    if len(hrv) >= 2 and hrv[0] < hrv[1]: rec_score -= 10
    if len(rhr) >= 2 and rhr[0] > rhr[1]: rec_score -= 10
    if len(sleep) >= 1 and sleep[0] < 7: rec_score -= 10

    zone = "Push" if rec_score >= 80 else "Maintain" if rec_score >= 60 else "Easy"
    km = "6–9 km Z2" if zone != "Push" else "7–10 km with strides"
    suggestion = (
        f"Recovery {rec_score}%. {zone} day. "
        f"Run: {km}. Keep cadence even; nasal breathing. "
        f"Hydrate and target protein. Sleep target 7h 45m."
    )

    return {
        "recovery": rec_score,
        "strain": zone,
        "sleepHours": round(sleep[0] if sleep else 0, 2),
        "sleepNeed": 7.75,
        "advice": suggestion,
        "latest": dict(latest) if latest else None
    }
