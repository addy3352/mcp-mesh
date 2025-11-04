import httpx
import os

MESH_URL = os.getenv("MESH_URL", "http://mcp-gateway:8090")

async def call_tool(tool, args=None, role="system"):
    args = args or {}
    async with httpx.AsyncClient() as client:
        r = await client.post(
            f"{MESH_URL}/mesh/call",
            json={"tool": tool, "args": args},
            headers={
                "X-Client-Role": role,
                "X-Client-Id": "mesh-scheduler"
            },
            timeout=60
        )
        r.raise_for_status()
        return r.json()
