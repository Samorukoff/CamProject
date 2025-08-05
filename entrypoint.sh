#!/bin/bash
set -e

echo "🟡 Waiting for DB to be ready..."
# ожидание подключения к базе
until pg_isready -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" > /dev/null 2>&1; do
  sleep 1
done

echo "✅ DB is ready. Running Alembic migrations..."
poetry run alembic upgrade head

echo "🚀 Starting application..."
exec poetry run uvicorn project.main:app --host 0.0.0.0 --port 8000