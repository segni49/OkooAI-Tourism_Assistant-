# 🛠️ Stage 1: Build environment
FROM python:3.11-slim AS builder

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency file first (better layer caching)
COPY requirements.txt .

# Upgrade pip and install dependencies
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# 🛡️ Stage 2: Runtime environment
FROM python:3.11-slim

# Create non-root user
RUN adduser --disabled-password --gecos "" okoo
USER okoo

WORKDIR /app

# Copy everything from builder
COPY --from=builder /app /app

# Set environment variable for Railway
ENV PORT=8000

# Expose FastAPI port
EXPOSE $PORT

# Start the FastAPI app (safe call via Python module)
CMD ["python", "-m", "uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
