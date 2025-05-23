# Generated by Django 5.1.4 on 2025-02-26 01:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ads', '0006_alter_necessidade_unidade'),
    ]

    operations = [
        migrations.AlterField(
            model_name='necessidade',
            name='unidade',
            field=models.CharField(choices=[('un', 'Unidade'), ('cx', 'Caixa'), ('pc', 'Peça'), ('kg', 'Kilograma'), ('m', 'Metro'), ('m2', 'Metro Quadrado'), ('m3', 'Metro Cúbico'), ('cm', 'Centímetro'), ('mm', 'Milímetro'), ('l', 'Litro'), ('g', 'Grama'), ('h', 'Hora'), ('d', 'Dia'), ('mês', 'Mês'), ('ano', 'Ano'), ('m²', 'Metro Quadrado'), ('m³', 'Metro Cúbico'), ('cm²', 'Centímetro Quadrado'), ('cm³', 'Centímetro Cúbico'), ('mm²', 'Milímetro Quadrado'), ('mm³', 'Milímetro Cúbico'), ('l', 'Litro'), ('ml', 'Mililitro'), ('g', 'Grama'), ('mg', 'Miligrama'), ('km', 'Quilograma'), ('h', 'Hora'), ('d', 'Dia'), ('mês', 'Mês'), ('ano', 'Ano')], default='Unidade', max_length=50),
        ),
    ]
