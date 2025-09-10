# 🐳 Lightweight Python base image
FROM python:3.11-alpine

# Set working directory
WORKDIR /app

# Install system dependencies for building Python packages
RUN apk add --no-cache \
    build-base \
    libffi-dev \
    openssl-dev \
    musl-dev \
    gcc \
    py3-pip

# Copy project files
COPY . /app

# Upgrade pip and install only core dependencies
COPY requirements.deploy.txt /app/requirements.txt
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Set environment variable for Railway
ENV PORT=8000

# Expose FastAPI port
EXPOSE $PORT

# Start the FastAPI app
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]