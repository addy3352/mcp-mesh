from fastapi import FastAPI
from recommend import recommend
import sqlite3, os

DB_PATH = os.getenv("SQLITE_PATH", "/data/mesh.db")

app = FastAPI(title="Mesh Core")

def db():
    return sqlite3.connect(DB_PATH)

@app.get("/mcp/tools")
def list_tools():
    return {"tools":[
        {"name":"core.get_health_summary", "description":"Returns daily vitals + last 7"}
    ]}

@app.post("/mcp/tool/core.get_health_summary")
def get_summary():
    conn = db()
    cur = conn.execute(
        "SELECT date, steps, calories, distance_km, sleep_hours, hrv_ms, rhr_bpm "
        "FROM garmin_daily ORDER BY date DESC LIMIT 7"
    )
    rows = [dict(zip(
        ["date","steps","cal","km","sleep","hrv","rhr"], r
    )) for r in cur.fetchall()]
    return {"result": rows}
