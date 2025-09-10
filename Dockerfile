# Base slim Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install dependencies for Ollama + Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    gcc \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Ollama
RUN curl -fsSL https://ollama.com/install.sh | sh

# Copy requirements and install them
COPY requirements.txt .
RUN pip install --upgrade pip setuptools wheel \
    && pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY api/ ./api/
COPY app/ ./app/
# COPY README.md ./README.md   # ❌ removed to avoid error

# Pull Ollama embedding model (smaller than LLMs)
RUN ollama pull nomic-embed-text

# Railway expects PORT
ENV PORT=8000

# Expose the port
EXPOSE 8000

# Start backend with uvicorn
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
