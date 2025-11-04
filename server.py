import sqlite3, os
from fastapi import FastAPI
from contextlib import asynccontextmanager
from scheduler import start_scheduler
from mcp.server.fastmcp import FastMCP # Assuming this is your final app object
# Note: Removed the unused/incorrect imports: mcp.server.fastmcp, tools, recommend

DB_PATH = os.getenv("SQLITE_PATH", "/data/mesh.db")
GLOBAL_SCHEDULER = None # Variable to hold the scheduler instance for shutdown

def db():
    # Helper function to get DB connection
    return sqlite3.connect(DB_PATH)

@asynccontextmanager
async def lifespan(app: FastAPI):
    global GLOBAL_SCHEDULER
    
    # STARTUP: Await the scheduler startup (start_scheduler must be made async)
    # This is the final step to fixing the RuntimeError
    GLOBAL_SCHEDULER = start_scheduler()
    print("Scheduler successfully started in async context.")
    
    yield # Application is now ready to receive requests
    
    # SHUTDOWN: Clean shutdown
    print("Shutting down APScheduler...")
    if GLOBAL_SCHEDULER:
        GLOBAL_SCHEDULER.shutdown() 
        print("APScheduler shut down.")

# 1. Initialize FastAPI using the lifespan manager (NO FastMCP)
app = FastAPI(title="Mesh Core", lifespan=lifespan)

# 1. Initialize FastAPI using the lifespan manager
#app = FastMCP(title="Mesh Core", 
#              tools=[get_health_summary],lifespan=lifespan)


@app.get("/mcp/tools")
def list_tools():
    # This is the tool list for the core service itself
    return {"tools":[
        {"name":"core.get_health_summary", "description":"Returns daily vitals + last 7"}
    ]}

@app.post("/mcp/tool/core.get_health_summary")
def get_summary():
    # This is the actual endpoint logic
    conn = db()
    conn.row_factory = sqlite3.Row # Ensure rows are dict-like
    cur = conn.execute(
        "SELECT date, steps, calories, distance_km, sleep_hours, hrv_ms, rhr_bpm "
        "FROM garmin_daily ORDER BY date DESC LIMIT 7"
    )
    # Note: Returning sqlite3.Row is fine, but for clean JSON, a dict is safer.
    rows = [dict(r) for r in cur.fetchall()] 
    return {"result": rows}