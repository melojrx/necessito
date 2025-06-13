from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ("budgets", "0010_drop_old_columns"),  # a migração anterior
    ]

    operations = [
        migrations.RunSQL(
            sql=[
                "ALTER TABLE budgets_orcamento "
                "DROP COLUMN IF EXISTS valor;"
            ],
            reverse_sql=migrations.RunSQL.noop,
        ),
    ]
