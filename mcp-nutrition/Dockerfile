FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y sqlite3 && rm -rf /var/lib/apt/lists/*
VOLUME ["/data"]

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
COPY ../notify.py .
COPY ../templates/ ./templates/

ENV PYTHONUNBUFFERED=1
EXPOSE 8003
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8003"]
