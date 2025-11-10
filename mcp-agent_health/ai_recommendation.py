from mcp_client import call_tool
from llm import get_llm_recommendation

async def compute_recommendation():
    # Fetch data from mesh-core DB via MCP tool
    data = await call_tool("core.get_health_summary")

    rows = data.get("result", [])
    print("No data in core.get_healthsummary {}".format(rows))
    if not rows:
        return {"error": "No data"}

    # Get recommendation from the LLM
    recommendation = await get_llm_recommendation(rows)

    return recommendation
