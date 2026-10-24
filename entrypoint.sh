#!/bin/sh

set -e

echo "Running migrations..."
poetry run alembic upgrade head

echo "Starting application..."
exec "$@"