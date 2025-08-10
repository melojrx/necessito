# budgets/migrations/0010_drop_old_columns.py
from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ("budgets", "0009_create_orcamentoitem_if_missing"),  # ← ajuste aqui
    ]

    operations = [
        migrations.RunSQL(
            sql=[
                "ALTER TABLE budgets_orcamento DROP COLUMN IF EXISTS descricao;",
                "ALTER TABLE budgets_orcamento DROP COLUMN IF EXISTS quantidade;",
                "ALTER TABLE budgets_orcamento DROP COLUMN IF EXISTS unidade;",
                "ALTER TABLE budgets_orcamento DROP COLUMN IF EXISTS marca;",
                
            ],
            reverse_sql=migrations.RunSQL.noop,
        ),
    ]
