
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os, httpx, sqlite3, json, time, yaml
from contextlib import contextmanager
from typing import Any
import os

POLICY_PATH = os.getenv("POLICY_CONFIG", "/app/policy.yaml")
AUDIT_DB     = os.getenv("AUDIT_DB_PATH", "/data/audit.db")
CHATGPT_SECRET_KEY = os.getenv("CHATGPT_SECRET_KEY") # Load from .env.mesh

app = FastAPI(title="MCP Gateway (Governance & Audit)")

origins = [o.strip() for o in os.getenv("CORS_ALLOW_ORIGINS", "").split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins or ["*"],  # tighten in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@contextmanager
def db():
    os.makedirs(os.path.dirname(AUDIT_DB), exist_ok=True)
    conn = sqlite3.connect(AUDIT_DB)
    conn.execute("""CREATE TABLE IF NOT EXISTS audit(
        id TEXT PRIMARY KEY,
        ts INTEGER,
        client_id TEXT,
        role TEXT,
        route TEXT,
        tool TEXT,
        args TEXT,
        decision TEXT
    );""")
    try:
        yield conn
    finally:
        conn.commit()
        conn.close()
def load_policy():
    with open(POLICY_PATH, "r") as f:
        return yaml.safe_load(f)

def redact(d: Any):
    if isinstance(d, dict):
        return {k: ("***" if k.lower() in {"token","password","access_token","bearer","authorization"} else redact(v)) for k, v in d.items()}
    if isinstance(d, list):
        return [redact(x) for x in d]
    return d

def record_audit(row):
    with db() as conn:
        conn.execute("INSERT OR REPLACE INTO audit VALUES(?,?,?,?,?,?,?,?)", row)

def allow_tool(policy, role: str, tool: str) -> bool:
    allow = set(policy.get("roles", {}).get(role, {}).get("allow_tools", []))
    deny  = set(policy.get("roles", {}).get(role, {}).get("deny_tools", []))
    if tool in deny:
        return False
    if allow and tool not in allow:
        return False
    return True


@app.get("/mesh/tools")
def list_tools(request: Request,key: str = Query(None)):
    policy = load_policy()
    if key == CHATGPT_SECRET_KEY:
        client_id = "chatgpt-connector" 
        role = "chatgpt-agent" # INJECT the authorized role
    else:
        client_id = request.headers.get("X-Client-Id", "unknown")
        role      = request.headers.get("X-Client-Role", "unknown")
    services = policy.get("services", {})
    out = []
    for svc, cfg in services.items():
        try:
            r = httpx.get(f"{cfg['url']}/mcp/tools", timeout=5.0)
            r.raise_for_status()
            tools = r.json().get("tools", [])
            for t in tools:
                if allow_tool(policy, role, t["name"]):
                    out.append({**t, "service": svc})
        except Exception:
            continue
    return {"client_id": client_id, "role": role, "tools": out}

class ToolCall(BaseModel):
    tool: str
    args: dict = {}
    route: str | None = None

@app.post("/mesh/call")
def call_tool(body: ToolCall, request: Request,key: str = Query(None)):  # <-- INJECT QUERY PARAM
    policy = load_policy()
    if key == CHATGPT_SECRET_KEY:
        client_id = "chatgpt-connector" 
        role = "chatgpt-agent" # INJECT the authorized role
    else:
        client_id = request.headers.get("X-Client-Id", "unknown")
        role      = request.headers.get("X-Client-Role", "unknown")
    tool = body.tool
    args = body.args or {}

    if not allow_tool(policy, role, tool):
        record_audit((f"audit-{time.time_ns()}", int(time.time()), client_id, role, body.route or "", tool, json.dumps(redact(args)), "deny"))
        raise HTTPException(status_code=403, detail=f"Tool '{tool}' not allowed for role '{role}'")

    svc = tool.split(".")[0]  # garmin | nutrition | linkedin | portal
    services = policy.get("services", {})
    if svc not in services:
        raise HTTPException(status_code=502, detail=f"Service for tool '{tool}' not configured")

    url = f"{services[svc]['url']}/mcp/tool/{tool}"
    try:
        r = httpx.post(url, json=args, timeout=60.0)
        r.raise_for_status()
        record_audit((f"audit-{time.time_ns()}", int(time.time()), client_id, role, body.route or "", tool, json.dumps(redact(args)), "allow"))
        try:
            return r.json()
        except Exception:
            return {"result": r.text}
    except httpx.HTTPError as e:
        raise HTTPException(status_code=502, detail=str(e))

@app.get("/audit/export")
def audit_export():
    with db() as conn:
        cur = conn.execute("SELECT id, ts, client_id, role, route, tool, args, decision FROM audit ORDER BY ts DESC LIMIT 10000")
        rows = [{"id": r[0], "ts": r[1], "client_id": r[2], "role": r[3], "route": r[4], "tool": r[5], "args": json.loads(r[6]), "decision": r[7]} for r in cur.fetchall()]
    return {"rows": rows}

@app.get("/ping")
def ping():
    return {"status": "ok", "service": "mcp-gateway"}
