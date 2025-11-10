FROM python:3.11-slim

WORKDIR /app

# Install requirements
COPY requirements.txt .
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir -r requirements.txt

# Copy gateway code
COPY . .

ENV PYTHONUNBUFFERED=1

EXPOSE 8090

CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8090"]
