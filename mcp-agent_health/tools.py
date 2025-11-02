from mcp.server import tool
from ..mesh.db import db
from ..notify import notify

@tool()
def get_health_metrics(days: int = 7):
    """
    Fetch last X days metrics for HRV, RHR, Sleep, Calories, Steps, Distance
    """
    with db() as conn:
        garmin = conn.execute(
            "SELECT date, hrv_ms, rhr_bpm, sleep_hours, steps, distance_km "
            "FROM garmin_daily ORDER BY date DESC LIMIT ?", (days,)
        ).fetchall()

        calories = conn.execute(
            "SELECT date, calories FROM calories_daily ORDER BY date DESC LIMIT ?", (days,)
        ).fetchall()

    return {
        "garmin": [dict(r) for r in garmin],
        "calories": [dict(r) for r in calories]
    }


@tool()
def save_recommendation(text: str):
    """Store AI generated recommendation"""
    with db() as conn:
        conn.execute("INSERT INTO events(type,message) VALUES (?,?)",
                     ("recommendation", text))
    return {"status": "saved"}


@tool()
def notify_health(text: str):
    """Send WhatsApp + Email to user"""
    notify("🏃‍♂️ Daily Health Coaching", text, etype="recommendation")
    return {"status": "sent"}


@tool()
def trigger_manual_sync():
    """UI button triggers Garmin + Nutrition via tools"""
    # Call your existing MCP tools
    # LLM chains them: garmin_sync + nutrition_sync
    return {"status": "agent_will_sync"}
