FROM python:3.11-bookworm

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y build-essential

# Copy project files
COPY . /app

# Upgrade pip and install dependencies
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Set environment variable for Railway
ENV PORT=8000

# Expose FastAPI port
EXPOSE $PORT

# Start the FastAPI app
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]