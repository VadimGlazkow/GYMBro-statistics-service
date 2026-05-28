#!/usr/bin/env bash
set -euo pipefail

echo "Running database migrations..."
alembic upgrade head
echo "Database migrations completed."

echo "Starting Statistics Service..."
exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8000}"
