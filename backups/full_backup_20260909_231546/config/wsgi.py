"""
WSGI config for config project.
"""

import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django

django.setup()

# Production safety:
# Ensure database migrations are applied even when the hosting
# platform starts Gunicorn directly instead of using start.sh.
try:
    from django.core.management import call_command
    from django.db import connection
    from accounts.models import Product

    print("===== WSGI DATABASE SAFETY CHECK =====")

    # Apply any pending migrations.
    call_command("migrate", interactive=False, verbosity=1)

    # Extra safety for the known missing Product table problem.
    table_name = Product._meta.db_table
    tables = connection.introspection.table_names()

    print(f"Product table: {table_name}")
    print(f"Product table exists: {table_name in tables}")

    if table_name not in tables:
        print("WARNING: Product table missing. Creating it now...")

        with connection.schema_editor() as schema_editor:
            schema_editor.create_model(Product)

        tables = connection.introspection.table_names()

    if table_name not in tables:
        raise RuntimeError(
            "FATAL: accounts_product table could not be created"
        )

    print("===== DATABASE SAFETY CHECK PASSED =====")

except Exception as exc:
    print("===== DATABASE STARTUP ERROR =====")
    print(repr(exc))
    raise

from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()
