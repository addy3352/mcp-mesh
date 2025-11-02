
# MCP Server Mesh (Ready-to-Run)

Services:
- gateway (governance + audit + filtered discovery)
- mcp-garmin (reads Garmin via garminconnect)
- mcp-nutrition (SQLite meal log + daily summary)
- mcp-linkedin (posts architecture updates)
- mcp-portal (updates your DO App health dashboard)

## Quick start (Docker)
1) Copy `.env.template` to `.env` and fill secrets.
2) `docker compose up -d`
3) Gateway:
   - Tools discovery (role-filtered): `GET http://localhost:8090/mesh/tools`
     - Add headers: `X-Client-Id`, `X-Client-Role`
   - Tool call: `POST http://localhost:8090/mesh/call` with JSON: `{"tool":"nutrition.get_daily_summary","args":{"date":"2025-10-31"}}`

## Roles
- chatgpt-agent: nutrition.write_meal, nutrition.get_daily_summary, nutrition.list_meals
- agent-iris: linkedin.create_post
- agent-health: garmin.* (read only), nutrition.get_daily_summary, portal.update_health_panel

Audit SQLite: `./gateway-data/audit.db`  
Nutrition SQLite: `./nutrition-data/nutrition.db`

## Mesh Docker File
| Feature                                | Enabled           |
| -------------------------------------- | ----------------- |
| SQLite persistent volume               | ✅ `/data/mesh.db` |
| Runs Uvicorn for mesh API              | ✅                 |
| Runs scheduler in same container       | ✅                 |
| Bootstraps DB if missing               | ✅                 |
| Designed for **mesh.aditya-raman.com** | ✅                 |

mcp-mesh/
 ├─ docker-compose.yml
 ├─ .env                     # DO droplet
 ├─ nginx.conf               # reverse proxy + CORS
 ├─ db/
 │   ├─ mesh.db
 │   └─ schema.sql
 ├─ gateway/
 │   ├─ server.py
 │   └─ policy.yaml
 ├─ mcp-garmin/
 │   ├─ server.py
 │   ├─ Dockerfile
 │   └─ requirements.txt
 ├─ mcp-nutrition/
 │   ├─ server.py
 │   ├─ Dockerfile
 │   └─ requirements.txt
 ├─ mcp-agent-health/
 │   ├─ server.py
 │   ├─ prompt.txt        ✅ move from readme.md
 │   ├─ README.md
 │   └─ Dockerfile
 ├─ mcp-linkedin/
 │   ├─ server.py
 │   └─ Dockerfile
 ├─ notify.py
 └─ requirements.txt        # global, if using monorepo pip
