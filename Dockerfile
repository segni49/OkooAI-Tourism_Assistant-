FROM python:3.14.0rc2-alpine3.22
WORKDIR /app
COPY . /app

# ✅ Add build tools including g++
RUN apk add --no-cache gcc g++ musl-dev libffi-dev

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

EXPOSE 8000
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]