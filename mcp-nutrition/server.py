
from fastapi import FastAPI
from router import router
from tools import list_tools
from db import init_db

app = FastAPI(title="MCP Nutrition Server")

@app.on_event("startup")
async def startup():
    await init_db()

@app.get("/ping")
async def ping():
    return {"status": "ok", "service": "mcp-nutrition"}

@app.get("/mcp/tools")
def mcp_tools():
    return {"tools": list_tools()}

app.include_router(router, prefix="/mcp/tool", tags=["mcp-tools"])
