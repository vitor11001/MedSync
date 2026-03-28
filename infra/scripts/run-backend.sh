#!/bin/bash

set -e

timestamp() {
  date +"%d/%m/%Y %H:%M:%S"
}

if [ -n "${DB_HOST}" ] && [ -n "${DB_PORT}" ]; then
  echo "$(timestamp) | Checking database connection ($DB_HOST:$DB_PORT) ..."
  while ! nc -z "$DB_HOST" "$DB_PORT"; do
    echo "$(timestamp) | Waiting for database..."
    sleep 2
  done
  echo "$(timestamp) | Database connection established"
fi

if [ "${RUN_MAKEMIGRATIONS}" = "true" ]; then
  echo "$(timestamp) | Generating migrations"
  python3 /app/src/manage.py makemigrations --noinput
  echo "$(timestamp) | Migrations generated"
fi

if [ "${RUN_MIGRATIONS}" = "true" ]; then
  echo "$(timestamp) | Applying migrations"
  python3 /app/src/manage.py migrate --noinput
  echo "$(timestamp) | Migrations applied"
fi

if [ "${CREATE_SUPERUSER}" = "true" ]; then
  echo "$(timestamp) | Ensuring default superuser"
  python3 /app/src/manage.py ensure_default_superuser
  echo "$(timestamp) | Superuser check completed"
fi

echo "$(timestamp) | Starting Django server on port ${APP_RUN_PORT:-8000}"
exec python3 /app/src/manage.py runserver 0.0.0.0:${APP_RUN_PORT:-8000}
