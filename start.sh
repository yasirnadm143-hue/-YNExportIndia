#!/bin/bash
set -e

echo "===== YN EXPORT INDIA START ====="

echo "===== APPLYING DATABASE MIGRATIONS ====="
python manage.py migrate --noinput

echo "===== COLLECTING STATIC FILES ====="
python manage.py collectstatic --noinput

if [ -n "${DJANGO_ADMIN_USERNAME:-}" ] && [ -n "${DJANGO_ADMIN_PASSWORD:-}" ]; then
    echo "===== SETTING UP ADMIN ====="
    python manage.py setup_admin
else
    echo "===== ADMIN ENV NOT SET - SKIPPING ADMIN SETUP ====="
fi

echo "===== STARTING GUNICORN ====="
exec gunicorn config.wsgi:application --bind 0.0.0.0:${PORT:-8000}
