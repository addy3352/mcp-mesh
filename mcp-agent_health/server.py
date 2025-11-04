# mcp-agent_health/server.py

from fastmcp import FastMCP
from mcp_client import call_tool

# ✅ Create MCP server instance
mcp = FastMCP(name="agent-health")


# ✅ MCP tools (proxy → mesh-core)
@mcp.tool()
async def get_health_metrics(days: int = 7):
    return await call_tool("core.get_health_summary", {"days": days}, role="agent-health")

@mcp.tool()
async def save_recommendation(text: str):
    return await call_tool("core.save_recommendation", {"text": text}, role="agent-health")

@mcp.tool()
async def notify_health(text: str):
    return await call_tool("core.notify_health", {"text": text}, role="agent-health")

@mcp.tool()
async def trigger_manual_sync():
    return await call_tool("core.trigger_manual_sync", role="agent-health")

# ✅ expose FastAPI app
app = mcp.app
