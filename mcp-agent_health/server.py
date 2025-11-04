# mcp-agent_health/server.py (FIXED)

from fastmcp import FastMCP
from mcp_client import call_tool
import asyncio

# --- 1. Instantiate FastMCP using the variable name 'app' ---
# FIX: The 'app' object IS the FastMCP instance itself.
app = FastMCP(name="agent-health")


# --- 2. MCP tools registered directly to the 'app' instance ---
# The decorator automatically registers the function with the app instance.
@app.tool()
async def get_health_metrics(days: int = 7):
    return await call_tool("core.get_health_summary", {"days": days}, role="agent-health")

@app.tool()
async def save_recommendation(text: str):
    return await call_tool("core.save_recommendation", {"text": text}, role="agent-health")

@app.tool()
async def notify_health(text: str):
    return await call_tool("core.notify_health", {"text": text}, role="agent-health")

@app.tool()
async def trigger_manual_sync():
    return await call_tool("core.trigger_manual_sync", role="agent-health")

# Note: The problematic line 'app = mcp.app' or 'app = mcp.fastapi_app' is now unnecessary and removed.