# mcp-agent_health/server.py (FIXED)

from fastapi import FastAPI
from fastmcp import FastMCP
from mcp_client import call_tool
from ai_recommendation import compute_recommendation
import asyncio

# --- 1. Instantiate FastMCP using the variable name 'mcp' ---
mcp = FastMCP(name="agent-health")


# --- 2. MCP tools registered directly to the 'mcp' instance ---
# The decorator automatically registers the function with the mcp instance.
print("I am in agnet_health before call tool mesh-core")
@mcp.tool()
async def get_health_metrics(days: int = 7):
    return await call_tool("core.get_health_summary", {"days": days}, role="agent-health")
print("I am in agnet_health after call tool and every thing is fine mwith mcp/call")


@mcp.tool()
async def save_recommendation(text: str):
    return await call_tool("core.save_recommendation", {"text": text}, role="agent-health")

@mcp.tool()
async def notify_health(text: str):
    return await call_tool("core.notify_health", {"text": text}, role="agent-health")

@mcp.tool()
async def trigger_manual_sync():
    return await call_tool("core.trigger_manual_sync", role="agent-health")

@mcp.tool()
async def get_ai_recommendation():
    """
    Computes and returns a personalized health recommendation using AI.
    """
    return await compute_recommendation()

# --- 3. Expose the FastAPI app instance for Uvicorn ---
root_app = FastAPI()
mcp_app = mcp.http_app()
root_app.mount("/mcp", mcp_app)

app = root_app