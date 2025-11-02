
from fastapi import FastAPI
from router import router
from tools import list_tools

app = FastAPI(title="MCP Garmin Server")

@app.get("/ping")
def ping():
    return {"status":"ok","service":"mcp-garmin"}

@app.get("/mcp/tools")
def tools():
    return {"tools": list_tools()}

app.include_router(router, prefix="/mcp/tool", tags=["garmin"])
