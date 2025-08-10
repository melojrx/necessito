# Generated manually for new budget model
# This migration restructures the Orcamento model to support multiple items

from django.db import migrations, models
import django.db.models.deletion
from decimal import Decimal
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('budgets', '0004_alter_orcamento_status'),
    ]

    operations = [
        # Remove campos antigos do modelo Orcamento
        migrations.RemoveField(
            model_name='orcamento',
            name='descricao',
        ),
        migrations.RemoveField(
            model_name='orcamento',
            name='quantidade',
        ),
        migrations.RemoveField(
            model_name='orcamento',
            name='unidade',
        ),
        migrations.RemoveField(
            model_name='orcamento',
            name='marca',
        ),
        migrations.RemoveField(
            model_name='orcamento',
            name='valor',
        ),
        
        # Alterar campo de status
        migrations.AlterField(
            model_name='orcamento',
            name='status',
            field=models.CharField(
                choices=[
                    ('pendente', 'Pendente'),
                    ('aguardando', 'Aguardando aceite do fornecedor'),
                    ('aceito', 'Aceito'),
                    ('rejeitado', 'Rejeitado')
                ],
                default='pendente',
                max_length=20
            ),
        ),
        
        # Alterar modificado_em para auto_now=True
        migrations.AlterField(
            model_name='orcamento',
            name='modificado_em',
            field=models.DateTimeField(auto_now=True),
        ),
        
        # Criar novo modelo OrcamentoItem
        migrations.CreateModel(
            name='OrcamentoItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tipo', models.CharField(choices=[('MAT', 'Material'), ('SRV', 'Serviço')], max_length=3)),
                ('descricao', models.CharField(max_length=255)),
                ('quantidade', models.DecimalField(decimal_places=3, max_digits=12, validators=[django.core.validators.MinValueValidator(Decimal('0.001'))])),
                ('unidade', models.CharField(max_length=10)),
                ('valor_unitario', models.DecimalField(decimal_places=2, max_digits=12, validators=[django.core.validators.MinValueValidator(Decimal('0.01'))])),
                ('ncm', models.CharField(blank=True, help_text='Nomenclatura Comum do Mercosul', max_length=10)),
                ('icms_percentual', models.DecimalField(blank=True, decimal_places=2, help_text='ICMS em percentual (0-100%)', max_digits=5, null=True, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)])),
                ('ipi_percentual', models.DecimalField(blank=True, decimal_places=2, help_text='IPI em percentual (0-100%)', max_digits=5, null=True, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)])),
                ('st_percentual', models.DecimalField(blank=True, decimal_places=2, help_text='Substituição Tributária em percentual (0-100%)', max_digits=5, null=True, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)])),
                ('difal_percentual', models.DecimalField(blank=True, decimal_places=2, help_text='DIFAL em percentual (0-100%)', max_digits=5, null=True, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)])),
                ('cnae', models.CharField(blank=True, help_text='Código CNAE do serviço', max_length=10)),
                ('aliquota_iss', models.DecimalField(blank=True, decimal_places=2, help_text='ISS em percentual (0-100%)', max_digits=5, null=True, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)])),
                ('orcamento', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='itens', to='budgets.orcamento')),
            ],
        ),
    ] 