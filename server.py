import sqlite3
import os
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastmcp import FastMCP
from scheduler import start_scheduler
from notify import notify
from mcp_client import call_tool

DB_PATH = os.getenv("SQLITE_PATH", "/data/mesh.db")
GLOBAL_SCHEDULER = None

def db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# 1. Create the FastMCP app instance first
mcp = FastMCP(name="mesh-core")

# ===================================================================
# ✅ MCP Tools (now registered with 'mcp' instance)
# ===================================================================

@mcp.tool()
def core_get_health_summary(days: int = 7):
    with db() as conn:
        rows = conn.execute("""
            SELECT date, steps, calories, distance_km, sleep_hours, hrv_ms, rhr_bpm
            FROM garmin_daily
            ORDER BY date DESC
            LIMIT ?
        """, (days,)).fetchall()
    print("if data is there {}".format(data))
    return {"data": [dict(r) for r in rows]}

@mcp.tool()
async def core_trigger_manual_sync():
    await asyncio.gather(
        call_tool("garmin.sync", role="system-manual-sync"),
        call_tool("nutrition.sync", role="system-manual-sync")
    )
    return {"status": "Garmin and Nutrition syncs triggered remotely via Mesh"}

@mcp.tool()
def core_save_recommendation(text: str):
    with db() as conn:
        conn.execute("INSERT INTO events(type, message) VALUES (?,?)",
                     ("recommendation", text))
    return {"status": "saved recommendation to DB"}

@mcp.tool()
def core_notify_health(text: str):
    notify(
        template_name="recommendation.txt",
        vars={"text": text},
        etype="agent_recommendation"
    )
    return {"status": "sent notification"}

# 2. Create the main FastAPI app
app = FastAPI(title="MCP Mesh Core")

# 3. Add the health check endpoint to the main FastAPI app
@app.get("/health")
def health_check():
    try:
        with db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='garmin_daily'")
            if cursor.fetchone():
                return {"status": "ok"}
            else:
                # Return 503 if the table doesn't exist, so the health check fails
                raise HTTPException(status_code=503, detail="Database not initialized")
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Database connection failed: {e}")

# ===================================================================
# ✅ Lifespan and DB Initialization
# ===================================================================

def init_db():
    db_dir = os.path.dirname(DB_PATH)
    os.makedirs(db_dir, exist_ok=True)
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='garmin_daily'")
        if not cursor.fetchone():
            print("Database tables not found. Initializing schema...")
            with open("db/schema.sql") as f:
                conn.executescript(f.read())
            print("Database initialized successfully.")
        conn.close()
    except Exception as e:
        print(f"Error during database initialization: {e}")
        raise

@asynccontextmanager
async def lifespan(app: FastAPI):
    global GLOBAL_SCHEDULER
    init_db()
    GLOBAL_SCHEDULER = await start_scheduler()
    print("Scheduler successfully started in async context.")
    yield
    print("Shutting down APScheduler...")
    if GLOBAL_SCHEDULER:
        GLOBAL_SCHEDULER.shutdown()
        print("APScheduler shut down.")

# Assign the lifespan to the main app
app.lifespan = lifespan

# 4. Mount the FastMCP app onto the main FastAPI app
# This makes all the @mcp.tool() endpoints available under the /mcp prefix
app.mount("/mcp", mcp.http_app())
