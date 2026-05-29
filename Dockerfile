FROM python:3.12-slim

ENV PYTHONPATH=/project
WORKDIR /project

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/
COPY logs/ ./logs/
COPY .env .

# Chainlit media
COPY public/ ./public/