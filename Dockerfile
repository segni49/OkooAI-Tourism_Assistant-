FROM python:3.11.8-slim-bookworm
WORKDIR /app
COPY . /app

# Install build tools
RUN apt-get update && apt-get install -y build-essential libffi-dev

# Install Python dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

EXPOSE 8000
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]