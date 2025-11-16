from fastapi import FastAPI, Request, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os, httpx, sqlite3, json, time, yaml
from contextlib import contextmanager
from typing import Any, Dict, Optional
from datetime import date

# --- Configuration ---
POLICY_PATH = os.getenv("POLICY_CONFIG", "/app/policy.yaml")
AUDIT_DB = os.getenv("AUDIT_DB_PATH", "/data/audit.db")
CHATGPT_SECRET_KEY = os.getenv("CHATGPT_SECRET_KEY")
HEALTH_KEY = os.getenv("AGENT_HEALTH_KEY")
AGENT_IRIS_KEY = os.getenv("AGENT_IRIS_KEY")
PORTAL_KEY = os.getenv("PORTAL_API_KEY")

# --- FastAPI App Initialization ---
app = FastAPI(title="MCP Gateway (Hybrid)", version="2.3.0")

origins = [o.strip() for o in os.getenv("CORS_ALLOW_ORIGINS", "").split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Database & Policy ---
@contextmanager
def db():
    os.makedirs(os.path.dirname(AUDIT_DB), exist_ok=True)
    conn = sqlite3.connect(AUDIT_DB)
    conn.execute("""CREATE TABLE IF NOT EXISTS audit(
        id TEXT PRIMARY KEY, ts INTEGER, client_id TEXT, role TEXT,
        route TEXT, tool TEXT, args TEXT, decision TEXT
    );""")
    try:
        yield conn
    finally:
        conn.commit()
        conn.close()

def load_policy():
    with open(POLICY_PATH, "r") as f:
        return yaml.safe_load(f)

# --- Helper Functions ---
def redact(d: Any):
    if isinstance(d, dict):
        return {k: ("***" if k.lower() in {"token", "password", "access_token", "bearer", "authorization"} else redact(v)) for k, v in d.items()}
    if isinstance(d, list):
        return [redact(x) for x in d]
    return d

def record_audit(row):
    with db() as conn:
        conn.execute("INSERT OR REPLACE INTO audit VALUES(?,?,?,?,?,?,?,?)", row)

# --- Refactored Authentication & Authorization ---
def identify_client(key: Optional[str], request: Request):
    # Try query parameter first
    if not key:
        # Fallback to header
        key = request.headers.get("X-API-KEY") or request.headers.get("x-api-key")
    
    if not key:
        raise HTTPException(status_code=401, detail="Missing API key")
    """Identifies the client and role based on the API key."""
    if key == CHATGPT_SECRET_KEY:
        return "chatgpt-connector", "chatgpt-agent"
    elif key == HEALTH_KEY:
        return "agent-health", "agent-health"
    elif key == PORTAL_KEY:
        return "portal-agent", "portal-agent"
    elif key == AGENT_IRIS_KEY:
        return "agent-iris", "agent-iris"
    else:
        # Fallback for old clients or other auth methods
        if key == HEALTH_KEY:
            print ("I am equal")
        else:
            print("key supplied is {} and length : {} and health_key is {} & length is {}  and are they equal {}".format(key, HEALTH_KEY,len(key),len(HEALTH_KEY),key == HEALTH_KEY))
        client_id = request.headers.get("X-Client-Id", "unknown")
        role = request.headers.get("X-Client-Role", "unknown")
        if client_id != "unknown":
            return client_id, role
        raise HTTPException(status_code=401, detail="Invalid or missing API key")

def allow_tool(policy, role: str, tool: str) -> bool:
    """Checks if a role is allowed to use a specific tool based on the policy."""
    role_policy = policy.get("roles", {}).get(role, {})
    allow = set(role_policy.get("allow_tools", []))
    deny = set(role_policy.get("deny_tools", []))
    
    if any(d.endswith('*') and tool.startswith(d[:-1]) for d in deny) or tool in deny:
        return False
    
    if not allow:
        return True
        
    if any(a.endswith('*') and tool.startswith(a[:-1]) for a in allow) or tool in allow:
        return True
        
    return False

# --- Generic Tool Call Function ---
async def call_tool(tool_name: str, args: Dict[str, Any], role: str):
    """
    Internal function to call any MCP tool.
    """
    policy = load_policy()

    if not allow_tool(policy, role, tool_name):
        raise HTTPException(status_code=403, detail=f"Tool '{tool_name}' not allowed for role '{role}'")

    svc = tool_name.split(".")[0]
    services = policy.get("services", {})
    if svc not in services:
        raise HTTPException(status_code=502, detail=f"Service '{svc}' for tool '{tool_name}' not configured")

    url = f"{services[svc]['url']}/mcp/call"
    payload = {"name": tool_name, "arguments": args}
    
    try:
        async with httpx.AsyncClient() as client:
            r = await client.post(url, json=payload, timeout=60.0)
            r.raise_for_status()
            return r.json()
    except httpx.HTTPError as e:
        raise HTTPException(status_code=502, detail=f"Error calling tool '{tool_name}': upstream service at '{url}' returned error: {e}")

# --- Portal API Endpoints ---
@app.post("/mcp/call/garmin/latest")
async def garmin_latest(request: Request, key: Optional[str]  = Query(None)):
    client_id, role = identify_client(key, request)
    # This should call mesh-core.get_health_summary, but we'll call garmin.get_stats for now
    # as mesh-core is not fully integrated yet.
    today_str = date.today().isoformat()
    data = await call_tool("garmin.get_stats", {"date": today_str}, role)
    return data

@app.get("/mcp/call/weight/latest")
async def weight_latest(request: Request, key: Optional[str] = Query(None)):
    client_id, role = identify_client(key, request)
    today_str = date.today().isoformat()
    return await call_tool("garmin.get_stats_and_body", {"date": today_str}, role)

@app.get("/mcp/call/calories/latest")
async def calories_latest(request: Request, key: Optional[str] = Query(None)):
    client_id, role = identify_client(key, request)
    today_str = date.today().isoformat()
    return await call_tool("nutrition.get_daily_summary", {"date": today_str}, role)

@app.post("/mcp/call/ai/recommendation")
async def ai_recommendation(request: Request, key: Optional[str] = Query(None)):
    client_id, role = identify_client(key, request)
    print("role is {}".format(role))
    return await call_tool("agent-health.get_ai_recommendation", {}, role)

@app.post("/mcp/call/sync/garmin")
async def sync_garmin(request: Request, key: Optional[str] = Query(None)):
    client_id, role = identify_client(key, request)
    return await call_tool("garmin.sync", {}, role)

@app.post("/mcp/call/sync/nutrition")
async def sync_nutrition(request: Request, key: Optional[str] = Query(None)):
    client_id, role = identify_client(key, request)
    return await call_tool("nutrition.sync", {}, role)

# --- Other Endpoints ---
@app.get("/audit/export")
def audit_export():
    with db() as conn:
        cur = conn.execute("SELECT id, ts, client_id, role, route, tool, args, decision FROM audit ORDER BY ts DESC LIMIT 10000")
        rows = [{"id": r[0], "ts": r[1], "client_id": r[2], "role": r[3], "route": r[4], "tool": r[5], "args": json.loads(r[6]), "decision": r[7]} for r in cur.fetchall()]
    return {"rows": rows}

@app.get("/ping")
def ping():
    return {"status": "ok", "service": "mcp-gateway"}
