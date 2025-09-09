# 🛠️ Stage 1: Build environment
FROM python:3.11.10-slim AS builder

WORKDIR /app

# Copy project files
COPY . /app

# Upgrade pip and install dependencies
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# 🧼 Optional: clean up cache
RUN rm -rf ~/.cache

# 🛡️ Stage 2: Runtime environment
FROM python:3.11.10-slim

# Create non-root user
RUN adduser --disabled-password --gecos "" okoo
USER okoo

WORKDIR /app

# Copy installed packages and app code from builder
COPY --from=builder /app /app

# Expose FastAPI port
EXPOSE 8000

# Start the FastAPI app
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]