import httpx
import os

MESH_CORE_URL = os.getenv("MESH_CORE_URL", "http://mesh-core:8091")

async def call_tool(tool, args=None, role="agent-health"):
    args = args or {}
    async with httpx.AsyncClient() as client:
        r = await client.post(
            f"{MESH_CORE_URL}/mcp/tool/{tool}",
            json=args,
            headers={
                "X-Client-Role": role,
                "X-Client-Id": "agent-health"
            },
            timeout=60
        )
        r.raise_for_status()
        return r.json()
