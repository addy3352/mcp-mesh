from mcp_client import call_tool

async def compute_recommendation():
    # Fetch data from mesh-core DB via MCP tool
    data = await call_tool("core.get_health_summary")

    rows = data.get("result", [])
    if not rows:
        return {"error": "No data"}

    # Extract values
    hrv = [r["hrv"] for r in rows]
    rhr = [r["rhr"] for r in rows]
    sleep = [r["sleep"] for r in rows]
    
    latest = rows[0]

    # simple heuristic (MVP WHOOP-style)
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
        "sleepHours": round(sleep[0], 2) if sleep else None,
        "sleepNeed": 7.75,
        "advice": suggestion,
        "latest": latest
    }
