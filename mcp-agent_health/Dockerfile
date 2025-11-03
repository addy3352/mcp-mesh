FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y sqlite3 && rm -rf /var/lib/apt/lists/*

VOLUME ["/data"]


COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONUNBUFFERED=1

EXPOSE 8008

CMD ["bash", "-c", "uvicorn server:app --host 0.0.0.0 --port 8008 & python agent.py"]