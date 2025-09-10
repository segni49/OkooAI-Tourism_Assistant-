FROM python:3.11-alpine

# Install build tools and system dependencies
RUN apk add --no-cache build-base libffi-dev

WORKDIR /app

# Copy project files
COPY . /app

# Upgrade pip and install dependencies
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Set environment variable for Railway
ENV PORT=8000

EXPOSE $PORT

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]