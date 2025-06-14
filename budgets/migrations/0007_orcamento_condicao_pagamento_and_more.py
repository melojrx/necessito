# Generated by Django 5.1.4 on 2025-06-08 02:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('budgets', '0006_alter_orcamento_observacao'),
    ]

    operations = [
        migrations.AddField(
            model_name='orcamento',
            name='condicao_pagamento',
            field=models.CharField(choices=[('a_vista', 'À vista'), ('entrada_saldo', '50% entrada + 50% na entrega'), ('parcelado_2x', 'Parcelado em 2x'), ('parcelado_3x', 'Parcelado em 3x'), ('parcelado_4x', 'Parcelado em 4x'), ('30_dias', '30 dias'), ('personalizado', 'Personalizado')], default='a_vista', max_length=20),
        ),
        migrations.AddField(
            model_name='orcamento',
            name='condicao_pagamento_personalizada',
            field=models.TextField(blank=True, help_text='Descreva a condição personalizada'),
        ),
        migrations.AddField(
            model_name='orcamento',
            name='forma_pagamento',
            field=models.CharField(choices=[('dinheiro', 'Dinheiro'), ('cartao_credito', 'Cartão de Crédito'), ('cartao_debito', 'Cartão de Débito'), ('pix', 'PIX'), ('boleto', 'Boleto'), ('transferencia', 'Transferência Bancária')], default='pix', max_length=20),
        ),
        migrations.AddField(
            model_name='orcamento',
            name='tipo_frete',
            field=models.CharField(choices=[('cif', 'CIF (Por conta do fornecedor)'), ('fob', 'FOB (Por conta do cliente)'), ('sem_frete', 'Sem frete')], default='fob', max_length=10),
        ),
        migrations.AddField(
            model_name='orcamento',
            name='tipo_venda',
            field=models.CharField(choices=[('revenda', 'Revenda'), ('uso_consumo', 'Uso e Consumo'), ('ativo_imobilizado', 'Ativo Imobilizado'), ('servico', 'Serviço')], default='uso_consumo', max_length=20),
        ),
        migrations.AddField(
            model_name='orcamento',
            name='valor_frete',
            field=models.DecimalField(blank=True, decimal_places=2, help_text='Valor do frete (se aplicável)', max_digits=10, null=True),
        ),
    ]
