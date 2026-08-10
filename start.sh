#!/bin/bash
set -e

echo "===== YN EXPORT INDIA START ====="

echo "===== APPLYING DATABASE MIGRATIONS ====="
python manage.py migrate --noinput

echo "===== COLLECTING STATIC FILES ====="
python manage.py collectstatic --noinput

echo "===== SETTING UP ADMIN ====="
python manage.py setup_admin

echo "===== STARTING GUNICORN ====="
exec gunicorn config.wsgi:application --bind 0.0.0.0:${PORT}
