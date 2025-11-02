from mcp.server.fastmcp import FastMCP
from . import tools

app = FastMCP(tools=[tools.get_health_metrics,
                     tools.save_recommendation,
                     tools.notify_health,
                     tools.trigger_manual_sync])
