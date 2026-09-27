FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code only (data directory is mounted via volume)
COPY main.py .
COPY app/ ./app/
COPY scripts/ ./scripts/
COPY sql/ ./sql/

# Set environment variables
ENV PYTHONUNBUFFERED=1

CMD ["python", "main.py"]
