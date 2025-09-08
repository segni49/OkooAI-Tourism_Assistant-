# ✅ Secure and minimal base image
FROM python:3.14.0rc2-alpine3.22

# Set working directory
WORKDIR /app

# Copy project files
COPY . /app

# Install build dependencies (for some Python packages)
RUN apk add --no-cache gcc musl-dev libffi-dev

# Install Python dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Expose FastAPI port
EXPOSE 8000

# Start FastAPI app
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]