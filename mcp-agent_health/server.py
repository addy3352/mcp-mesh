from fastapi import FastAPI, HTTPException
from fastmcp import FastMCP
from pydantic import BaseModel
from typing import Dict, Any, Optional
from mcp_client import call_tool
from ai_recommendation import compute_recommendation

# Create FastMCP instance (for future MCP client use)
mcp = FastMCP(name="agent-health")

print("=== Agent Health Service Starting ===")

# Register MCP tools (these are callable as functions internally)
@mcp.tool()
async def get_health_metrics(days: int = 7):
    """Get health summary for specified number of days"""
    return await call_tool("core.get_health_summary", {"days": days}, role="agent-health")

@mcp.tool()
async def save_recommendation(text: str):
    """Save a health recommendation"""
    return await call_tool("core.save_recommendation", {"text": text}, role="agent-health")

@mcp.tool()
async def notify_health(text: str):
    """Send health notification"""
    return await call_tool("core.notify_health", {"text": text}, role="agent-health")

@mcp.tool()
async def trigger_manual_sync():
    """Trigger manual data synchronization"""
    return await call_tool("core.trigger_manual_sync", role="agent-health")

@mcp.tool()
async def get_ai_recommendation():
    """Computes and returns a personalized health recommendation using AI"""
    print("=== Computing AI recommendation ===")
    return await compute_recommendation()

print("✓ 5 MCP tools registered")

# Create FastAPI app with REST endpoints
app = FastAPI(title="Agent Health Service", version="1.0.0")

# Pydantic model for tool calls
class ToolCallRequest(BaseModel):
    name: str
    arguments: Optional[Dict[str, Any]] = {}

# REST API endpoint to call tools
@app.post("/mcp/call")
async def call_mcp_tool(request: ToolCallRequest):
    """Call an MCP tool via REST API"""
    print(f"[REST] Tool call received: {request.name}")
    
    # Map tool names to functions
    tool_map = {
        "agent-health.get_health_metrics": get_health_metrics,
        "agent-health.save_recommendation": save_recommendation,
        "agent-health.notify_health": notify_health,
        "agent-health.trigger_manual_sync": trigger_manual_sync,
        "agent-health.get_ai_recommendation": get_ai_recommendation,
    }
    
    if request.name not in tool_map:
        raise HTTPException(status_code=404, detail=f"Tool not found: {request.name}")
    
    try:
        # Call the tool function
        tool_func = tool_map[request.name]
        result = await tool_func.fn(**request.arguments)
        return {"result": result, "tool": request.name}
    except Exception as e:
        print(f"[REST] Tool call error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# List all available tools
@app.get("/mcp/tools")
async def list_tools():
    """List all available MCP tools"""
    return {
        "tools": [
            {
                "name": "agent-health.get_health_metrics",
                "description": "Get health summary for specified number of days",
                "parameters": {"days": "int (default: 7)"}
            },
            {
                "name": "agent-health.save_recommendation",
                "description": "Save a health recommendation",
                "parameters": {"text": "str"}
            },
            {
                "name": "agent-health.notify_health",
                "description": "Send health notification",
                "parameters": {"text": "str"}
            },
            {
                "name": "agent-health.trigger_manual_sync",
                "description": "Trigger manual data synchronization",
                "parameters": {}
            },
            {
                "name": "agent-health.get_ai_recommendation",
                "description": "Computes and returns a personalized health recommendation using AI",
                "parameters": {}
            }
        ]
    }

# Health check endpoints
@app.get("/")
async def root():
    return {
        "service": "agent-health",
        "status": "running",
        "version": "1.0.0",
        "tools_count": 5
    }

@app.get("/ping")
async def ping():
    return {"status": "ok"}

print("=== Agent Health Service Ready ===")
print("✓ REST API available:")
print("  - GET  / (service info)")
print("  - GET  /ping (health check)")
print("  - GET  /mcp/tools (list tools)")
print("  - POST /mcp/call (call tool)")