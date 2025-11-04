from fastapi import FastAPI
from mcp.server.fastmcp import FastMCP
from contextlib import asynccontextmanager
import sqlite3, os
from scheduler import start_scheduler

DB_PATH = os.getenv("SQLITE_PATH", "/data/mesh.db")

app = FastAPI(title="Mesh Core")


def db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# MCP tool: core health summary
def core_get_health_summary(days: int = 7):
    with db() as conn:
        rows = conn.execute("""
            SELECT date, steps, calories, distance_km, sleep_hours, hrv_ms, rhr_bpm
            FROM garmin_daily ORDER BY date DESC LIMIT ?
        """, (days,)).fetchall()

    return [dict(r) for r in rows]


@asynccontextmanager
async def lifespan(app):
    global GLOBAL_SCHEDULER
    
    # FIX: Await the scheduler startup and store the instance
    GLOBAL_SCHEDULER = await start_scheduler()
    print("Scheduler successfully started in async context.")
    
    yield # Application is now ready to receive requests
    
    # FIX: Clean shutdown when the server is closing
    print("Shutting down APScheduler...")
    if GLOBAL_SCHEDULER:
        GLOBAL_SCHEDULER.shutdown() 
        print("APScheduler shut down.")

    # Start APScheduler when API starts
#    start_scheduler()
#    yield
    # (Optionally clean shutdown code later)

app = FastMCP(
    tools=[core_get_health_summary],
    lifespan=lifespan
)



