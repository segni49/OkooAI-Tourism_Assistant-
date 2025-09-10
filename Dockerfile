# 🛠️ Stage 1: Build environment
FROM python:3.11-bookworm AS builder

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y build-essential

# Copy project files
COPY . /app

# Upgrade pip and install dependencies
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# 🧼 Optional: clean up cache
RUN rm -rf ~/.cache

# 🛡️ Stage 2: Runtime environment
FROM python:3.11-bookworm

# Create non-root user
RUN adduser --disabled-password --gecos "" okoo
USER okoo

WORKDIR /app

# Copy app code
COPY --from=builder /app /app

# Reinstall uvicorn explicitly in runtime stage
RUN pip install --no-cache-dir uvicorn

# Set environment variables
ENV PORT=8000

# Expose FastAPI port
EXPOSE $PORT

# Start the FastAPI app
ENTRYPOINT ["uvicorn"]
CMD ["api.main:app", "--host", "0.0.0.0", "--port", "8000"]