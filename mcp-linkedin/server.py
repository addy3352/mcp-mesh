
from fastapi import FastAPI
from router import router
from tools import list_tools

app = FastAPI(title="MCP LinkedIn Server")

@app.get("/ping")
def ping():
    return {"status":"ok","service":"mcp-linkedin"}

@app.get("/mcp/tools")
def mcp_tools():
    return {"tools": list_tools()}

app.include_router(router, prefix="/mcp/tool", tags=["mcp-tools"])
