import httpx, os

MESH_URL = os.getenv("MCP_GATEWAY_URL")
MESH_TOKEN = os.getenv("MCP_KEY")

async def call_mcp_tool(service, tool, args):
    async with httpx.AsyncClient() as client:
        r = await client.post(
            f"{MESH_URL}/tools/{service}/{tool}",
            headers={"Authorization": f"Bearer {MESH_TOKEN}"},
            json=args
        )
        r.raise_for_status()
        return r.json()
