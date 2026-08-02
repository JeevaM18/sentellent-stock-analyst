#!/bin/sh
set -e

echo "======================================"
echo "Running database migrations..."
echo "======================================"
alembic upgrade head

echo "======================================"
echo "Seeding companies..."
echo "======================================"
python -m app.scripts.seed_companies

echo "======================================"
echo "Ingesting company fundamentals..."
echo "======================================"
python -m app.scripts.ingest_fundamentals

echo "======================================"
echo "Starting FastAPI..."
echo "======================================"
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
