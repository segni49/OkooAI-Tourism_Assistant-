# 🐍 Use lightweight Python base image
FROM python:3.11-slim


WORKDIR /app

# Install only what’s needed to build light deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy only requirements first (better layer caching)
COPY requirements.txt .

# Install Python deps (with cache disabled to reduce size)
RUN pip install --upgrade pip setuptools wheel \
    && pip install --no-cache-dir -r requirements.txt

# Copy only necessary source files
COPY api/ ./api/
COPY app/ ./app/
COPY README.md ./README.md

# Railway expects PORT env variable
ENV PORT=8000

# Expose FastAPI port
EXPOSE $PORT

# Start FastAPI (backend)
CMD ["python", "-m", "uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
