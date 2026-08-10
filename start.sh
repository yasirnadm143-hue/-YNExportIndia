#!/bin/bash
set -e

echo "======================================"
echo "       YN EXPORT INDIA START"
echo "======================================"

echo "===== 1. DATABASE MIGRATIONS ====="
python manage.py migrate --noinput

echo "===== 2. CHECKING PRODUCT TABLE ====="

PRODUCT_TABLE=$(python manage.py shell -c "
from django.db import connection
tables = connection.introspection.table_names()
print('YES' if 'accounts_product' in tables else 'NO')
" | tail -n 1)

echo "accounts_product table: $PRODUCT_TABLE"

if [ "$PRODUCT_TABLE" = "NO" ]; then
    echo "===== PRODUCT TABLE MISSING ====="
    echo "===== REPAIRING MIGRATION 0007 ====="

    python manage.py migrate accounts 0006 --fake
    python manage.py migrate accounts 0007 --noinput

    echo "===== VERIFYING PRODUCT TABLE ====="

    PRODUCT_TABLE=$(python manage.py shell -c "
from django.db import connection
tables = connection.introspection.table_names()
print('YES' if 'accounts_product' in tables else 'NO')
" | tail -n 1)

    if [ "$PRODUCT_TABLE" != "YES" ]; then
        echo "ERROR: accounts_product table could not be created."
        exit 1
    fi

    echo "SUCCESS: accounts_product table exists."
else
    echo "SUCCESS: accounts_product table already exists."
fi

echo "===== 3. COLLECT STATIC ====="
python manage.py collectstatic --noinput

echo "===== 4. ADMIN SETUP ====="

if [ -n "${DJANGO_ADMIN_USERNAME:-}" ] && [ -n "${DJANGO_ADMIN_PASSWORD:-}" ]; then
    python manage.py setup_admin
else
    echo "ADMIN ENV NOT SET - SKIPPING ADMIN SETUP"
fi

echo "===== 5. FINAL DATABASE CHECK ====="
python manage.py check

echo "===== 6. STARTING GUNICORN ====="
exec gunicorn config.wsgi:application --bind 0.0.0.0:${PORT:-8000}
