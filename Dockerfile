# 🛠️ Base image (lightweight + better prebuilt wheels support)
FROM python:3.11-slim-bullseye

# Set working directory
WORKDIR /app

# Install system dependencies required for some Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy only requirements first (better caching)
COPY requirements.txt .

# Upgrade pip and install dependencies
RUN pip install --upgrade pip setuptools wheel \
    && pip install --no-cache-dir -r requirements.txt

# Copy project files (after deps installed)
COPY . .

# Railway expects PORT env variable
ENV PORT=8000

# Expose FastAPI port
EXPOSE $PORT

# Start FastAPI using uvicorn
CMD ["python", "-m", "uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
