#!/bin/sh
set -e

echo "Running database migrations..."
alembic upgrade head

echo "Seeding company master data..."
python -m app.scripts.seed_companies || echo "Seeding completed or already populated."

echo "Starting FastAPI application..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
