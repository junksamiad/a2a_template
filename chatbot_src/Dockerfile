FROM python:3.12-slim

WORKDIR /app

# Install system deps (if any)
RUN apt-get update && apt-get install -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# Copy code
COPY . /app

# Install Python deps
RUN pip install --no-cache-dir -r requirements-a2a.txt

EXPOSE 8080

CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8080"] 