#!/bin/bash
set -e

echo "======================================"
echo "       YN EXPORT INDIA START"
echo "======================================"

echo "===== 1. APPLYING ALL MIGRATIONS ====="
python manage.py migrate --noinput

echo "===== 2. FINAL PRODUCT TABLE SAFETY CHECK ====="

python manage.py shell <<'PY'
from django.db import connection
from accounts.models import Product

table_name = Product._meta.db_table
tables = connection.introspection.table_names()

print("Product table:", table_name)

if table_name not in tables:
    print("WARNING: Product table is still missing.")
    print("Creating it directly with Django schema editor...")

    with connection.schema_editor() as schema_editor:
        schema_editor.create_model(Product)

    tables = connection.introspection.table_names()

if table_name not in tables:
    raise RuntimeError("FATAL: accounts_product could not be created")

print("SUCCESS: accounts_product exists")
PY

echo "===== 3. COLLECTING STATIC FILES ====="
python manage.py collectstatic --noinput

echo "===== 4. ADMIN SETUP ====="

if [ -n "${DJANGO_ADMIN_USERNAME:-}" ] && [ -n "${DJANGO_ADMIN_PASSWORD:-}" ]; then
    python manage.py setup_admin

    echo "===== 4B. VERIFYING ADMIN LOGIN CREDENTIALS ====="
    python manage.py shell -c "
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate
User = get_user_model()
username = '${DJANGO_ADMIN_USERNAME}'
password = '${DJANGO_ADMIN_PASSWORD}'
u = User.objects.filter(username=username).first()
print('ADMIN USER EXISTS:', bool(u))
if u:
    print('ADMIN ACTIVE:', u.is_active)
    print('ADMIN STAFF:', u.is_staff)
    print('ADMIN SUPERUSER:', u.is_superuser)
    print('PASSWORD HASH VALID:', u.check_password(password))
    a = authenticate(username=username, password=password)
    print('AUTHENTICATION RESULT:', bool(a))
    if not a:
        raise RuntimeError('FATAL: Admin authentication verification failed')
"
else
    echo "ADMIN ENV NOT SET - SKIPPING ADMIN SETUP"
fi

echo "===== 5. DJANGO SYSTEM CHECK ====="
python manage.py check

echo "===== 6. STARTING GUNICORN ====="
exec gunicorn config.wsgi:application --bind 0.0.0.0:${PORT:-8000}
