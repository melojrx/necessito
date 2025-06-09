from django.db import migrations

SQL_CREATE_TABLE = """
CREATE TABLE IF NOT EXISTS budgets_orcamentoitem (
    id BIGSERIAL PRIMARY KEY,
    tipo VARCHAR(3) NOT NULL,
    descricao VARCHAR(255) NOT NULL,
    quantidade NUMERIC(12,3) NOT NULL,
    unidade VARCHAR(10) NOT NULL,
    valor_unitario NUMERIC(12,2) NOT NULL,
    ncm VARCHAR(10),
    icms_percentual NUMERIC(5,2),
    ipi_percentual NUMERIC(5,2),
    st_percentual NUMERIC(5,2),
    difal_percentual NUMERIC(5,2),
    cnae VARCHAR(10),
    aliquota_iss NUMERIC(5,2),
    orcamento_id BIGINT NOT NULL REFERENCES budgets_orcamento(id) DEFERRABLE INITIALLY DEFERRED
);
CREATE INDEX IF NOT EXISTS budgets_orcamentoitem_orcamento_id_idx ON budgets_orcamentoitem (orcamento_id);
"""


def forwards(apps, schema_editor):
    schema_editor.execute(SQL_CREATE_TABLE)


def backwards(apps, schema_editor):
    # Não removemos a tabela em reversão para evitar perda de dados.
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("budgets", "0008_alter_orcamento_condicao_pagamento_and_more"),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ] 