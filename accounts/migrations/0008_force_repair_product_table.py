from django.db import migrations


def ensure_product_table(apps, schema_editor):
    Product = apps.get_model("accounts", "Product")
    table_name = Product._meta.db_table

    existing_tables = schema_editor.connection.introspection.table_names()

    if table_name not in existing_tables:
        print(f"REPAIR: creating missing table {table_name}")
        schema_editor.create_model(Product)
        print(f"REPAIR: {table_name} created successfully")
    else:
        print(f"REPAIR: {table_name} already exists")


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0007_repair_product_table"),
    ]

    operations = [
        migrations.RunPython(
            ensure_product_table,
            migrations.RunPython.noop,
        ),
    ]
