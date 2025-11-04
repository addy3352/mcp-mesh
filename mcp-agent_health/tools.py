from fastmcp import FastMCP
from mcp_client import call_tool

mcp = FastMCP(name="agent-health")

@mcp.tool
async def get_health_metrics(days: int = 7):
    return await call_tool("core.get_health_metrics", {"days": days})

@mcp.tool
async def save_recommendation(text: str):
    return await call_tool("core.save_recommendation", {"text": text})

@mcp.tool
async def notify_health(text: str):
    return await call_tool("core.notify_health", {"text": text})

@mcp.tool
async def trigger_manual_sync():
    return await call_tool("core.trigger_manual_sync")
