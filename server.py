import sqlite3
import os
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastmcp import FastMCP
from scheduler import start_scheduler
from notify import notify
from mcp_client import call_tool
from pydantic import BaseModel
from typing import Dict, Any, Optional

# --- Configuration ---
DB_PATH = os.getenv("SQLITE_PATH", "/data/mesh.db")
GLOBAL_SCHEDULER = None

# --- Database Helper ---
def db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# --- FastMCP Instance ---
mcp = FastMCP(name="mesh-core")

# --- Tool Functions ---
@mcp.tool()
def core_get_health_summary(days: int = 7):
    with db() as conn:
        rows = conn.execute("""
            SELECT date, steps, calories, distance_km, sleep_hours, hrv_ms, rhr_bpm
            FROM garmin_daily
            ORDER BY date DESC
            LIMIT ?
        """, (days,)).fetchall()
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

# --- FastAPI App Initialization ---
app = FastAPI(title="MCP Mesh Core (Refactored)", version="2.0.0")

# --- Pydantic Models ---
class ToolCallRequest(BaseModel):
    name: str
    arguments: Optional[Dict[str, Any]] = {}

# --- Manual MCP Endpoints ---
@app.post("/mcp/call")
async def call_mcp_tool(request: ToolCallRequest):
    """Call a mesh-core tool via REST API"""
    tool_map = {
        "mesh-core.core_get_health_summary": core_get_health_summary,
        "mesh-core.core_trigger_manual_sync": core_trigger_manual_sync,
        "mesh-core.core_save_recommendation": core_save_recommendation,
        "mesh-core.core_notify_health": core_notify_health,
    }
    
    if request.name not in tool_map:
        raise HTTPException(status_code=404, detail=f"Tool not found: {request.name}")
    
    try:
        tool_func = tool_map[request.name]
        # Check if the function is async
        if asyncio.iscoroutinefunction(tool_func.fn):
            result = await tool_func.fn(**request.arguments)
        else:
            result = tool_func.fn(**request.arguments)
        return {"result": result, "tool": request.name}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/mcp/tools")
async def list_tools():
    """List all available mesh-core tools"""
    return {
        "tools": [
            {
                "name": "mesh-core.core_get_health_summary",
                "description": "Get health summary for a specified number of days.",
                "parameters": {"days": "int (default: 7)"}
            },
            {
                "name": "mesh-core.core_trigger_manual_sync",
                "description": "Trigger manual data synchronization for Garmin and Nutrition.",
                "parameters": {}
            },
            {
                "name": "mesh-core.core_save_recommendation",
                "description": "Save a health recommendation to the database.",
                "parameters": {"text": "str"}
            },
            {
                "name": "mesh-core.core_notify_health",
                "description": "Send a health notification.",
                "parameters": {"text": "str"}
            }
        ]
    }

# --- Health Check & Lifespan ---
@app.get("/health")
def health_check():
    try:
        with db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='garmin_daily'")
            if cursor.fetchone():
                return {"status": "ok"}
            else:
                raise HTTPException(status_code=503, detail="Database not initialized")
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Database connection failed: {e}")

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

app.lifespan = lifespan