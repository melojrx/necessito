# Generated by Django 5.1.4 on 2025-02-24 02:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('budgets', '0003_orcamento_modificado_em'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orcamento',
            name='status',
            field=models.CharField(choices=[('pendente', 'Pendente'), ('Aguardando aceite do fornecedor', 'Aguardando aceite do fornecedor'), ('aceito', 'Aceito'), ('rejeitado', 'Rejeitado')], default='pendente', max_length=50),
        ),
    ]
