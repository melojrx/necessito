# Generated manually for populating states
from django.db import migrations

def populate_states(apps, schema_editor):
    State = apps.get_model('search', 'State')
    
    estados_brasileiros = [
        ('Acre', 'AC'),
        ('Alagoas', 'AL'),
        ('Amapá', 'AP'),
        ('Amazonas', 'AM'),
        ('Bahia', 'BA'),
        ('Ceará', 'CE'),
        ('Distrito Federal', 'DF'),
        ('Espírito Santo', 'ES'),
        ('Goiás', 'GO'),
        ('Maranhão', 'MA'),
        ('Mato Grosso', 'MT'),
        ('Mato Grosso do Sul', 'MS'),
        ('Minas Gerais', 'MG'),
        ('Pará', 'PA'),
        ('Paraíba', 'PB'),
        ('Paraná', 'PR'),
        ('Pernambuco', 'PE'),
        ('Piauí', 'PI'),
        ('Rio de Janeiro', 'RJ'),
        ('Rio Grande do Norte', 'RN'),
        ('Rio Grande do Sul', 'RS'),
        ('Rondônia', 'RO'),
        ('Roraima', 'RR'),
        ('Santa Catarina', 'SC'),
        ('São Paulo', 'SP'),
        ('Sergipe', 'SE'),
        ('Tocantins', 'TO'),
    ]
    
    for nome, sigla in estados_brasileiros:
        State.objects.get_or_create(
            abbreviation=sigla,
            defaults={'name': nome}
        )

def reverse_populate_states(apps, schema_editor):
    State = apps.get_model('search', 'State')
    State.objects.all().delete()

class Migration(migrations.Migration):

    dependencies = [
        ('search', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(
            populate_states,
            reverse_populate_states,
        ),
    ] 