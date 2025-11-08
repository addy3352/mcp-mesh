import sqlite3
import os
import asyncio
from contextlib import asynccontextmanager
from fastmcp import FastMCP
from scheduler import start_scheduler
from notify import notify  # Need to import notify
from mcp_client import call_tool # Needed to trigger remote syncs

DB_PATH = os.getenv("SQLITE_PATH", "/data/mesh.db")
GLOBAL_SCHEDULER = None # Global to hold the scheduler instance

def db():
    # Helper function to get DB connection (using built-in sqlite3, not db/db.py)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# ✅ FastMCP app
app = FastMCP(name="mesh-core")

# ===================================================================
# ✅ MCP Tools
# ===================================================================

@app.tool()
def core_get_health_summary(days: int = 7):
    # Data retrieval for Agent-Health (and others)
    with db() as conn:
        rows = conn.execute("""
            SELECT date, steps, calories, distance_km, sleep_hours, hrv_ms, rhr_bpm
            FROM garmin_daily
            ORDER BY date DESC
            LIMIT ?
        """, (days,)).fetchall()
    return {"data": [dict(r) for r in rows]}

@app.tool()
async def core_trigger_manual_sync():
    # Use mcp_client to trigger the remote sync tools in other services
    # This replaces core_garmin_sync and core_nutrition_sync for better service separation
    await asyncio.gather(
        call_tool("garmin.sync", role="system-manual-sync"),
        call_tool("nutrition.sync", role="system-manual-sync")
    )
    return {"status": "Garmin and Nutrition syncs triggered remotely via Mesh"}

@app.tool()
def core_save_recommendation(text: str):
    # Saves the recommendation text into the events table
    with db() as conn:
        conn.execute("INSERT INTO events(type, message) VALUES (?,?)",
                     ("recommendation", text))
    return {"status": "saved recommendation to DB"}

@app.tool()
def core_notify_health(text: str):
    # Uses notify.py to send the message (e.g., via WhatsApp)
    notify(
        template_name="recommendation.txt", # Placeholder template for general text
        vars={"text": text},
        etype="agent_recommendation"
    )
    return {"status": "sent notification"}

# ===================================================================
# ✅ Access Control (Core tools only accessible to Agent-Health)
# ===================================================================

#app.allow("agent-health", "core_get_health_summary")
#app.allow("agent-health", "core_trigger_manual_sync") # Previously core_garmin_sync/nutrition_sync
#app.allow("agent-health", "core_save_recommendation")
#app.allow("agent-health", "core_notify_health")

# ===================================================================
# ✅ Start scheduler inside lifespan (FIXED: Await + Shutdown)
# ===================================================================

def init_db():
    """
    Initializes the database by creating tables from the schema.sql file
    if the tables do not already exist.
    """
    db_dir = os.path.dirname(DB_PATH)
    os.makedirs(db_dir, exist_ok=True)
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Check if the 'garmin_daily' table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='garmin_daily'")
        table_exists = cursor.fetchone()
        
        if not table_exists:
            print("Database tables not found. Initializing schema...")
            with open("db/schema.sql") as f:
                conn.executescript(f.read())
            print("Database initialized successfully.")
        
        conn.close()
    except Exception as e:
        print(f"Error during database initialization: {e}")
        raise

@asynccontextmanager
async def lifespan(app):
    global GLOBAL_SCHEDULER
    
    # STARTUP: Initialize DB and then start scheduler
    init_db()
    GLOBAL_SCHEDULER = await start_scheduler()
    print("Scheduler successfully started in async context.")

    yield # Application is now ready to receive requests

    # SHUTDOWN: Clean shutdown
    print("Shutting down APScheduler...")
    if GLOBAL_SCHEDULER:
        GLOBAL_SCHEDULER.shutdown()
        print("APScheduler shut down.")

app.lifespan = lifespan