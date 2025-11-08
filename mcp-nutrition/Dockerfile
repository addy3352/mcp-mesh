FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y sqlite3 && rm -rf /var/lib/apt/lists/*
VOLUME ["/data"]

COPY mcp-nutrition/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# --- Copy Source Files ---
# Fix: Reference internal db.py relative to root context
COPY mcp-nutrition/nutrition_db.py .

# CRITICAL FIX: Explicitly copy Python source files required by the app
COPY mcp-nutrition/server.py .
COPY mcp-nutrition/router.py .
COPY mcp-nutrition/nutrition_sync.py .
COPY mcp-nutrition/models.py .
COPY mcp-nutrition/auth.py .
COPY mcp-nutrition/tools.py .

# Copy external files directly from root context (as they were before)
COPY notify.py .
COPY templates/ ./templates/

ENV PYTHONUNBUFFERED=1
EXPOSE 8003
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8003"]