from django.db import migrations


def repair_product_table(apps, schema_editor):
    Product = apps.get_model("accounts", "Product")

    existing_tables = schema_editor.connection.introspection.table_names()

    if Product._meta.db_table not in existing_tables:
        schema_editor.create_model(Product)


def reverse_repair_product_table(apps, schema_editor):
    Product = apps.get_model("accounts", "Product")

    existing_tables = schema_editor.connection.introspection.table_names()

    if Product._meta.db_table in existing_tables:
        schema_editor.delete_model(Product)


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0006_customuser_active_downline_count_and_more"),
    ]

    operations = [
        migrations.RunPython(
            repair_product_table,
            reverse_repair_product_table,
        ),
    ]
