# Generated manually for populating existing necessidades with user address

from django.db import migrations

def populate_existing_necessidades_with_user_address(apps, schema_editor):
    """
    Preenche necessidades existentes com endereço do usuário
    """
    Necessidade = apps.get_model('ads', 'Necessidade')
    
    updated_count = 0
    
    for necessidade in Necessidade.objects.all():
        user = necessidade.cliente
        
        # Configurar para usar endereço do usuário por padrão
        necessidade.usar_endereco_usuario = True
        
        # Copiar dados do usuário para campos específicos do serviço
        necessidade.cidade_servico = user.cidade or 'Não informado'
        necessidade.estado_servico = user.estado or 'SP'
        necessidade.cep_servico = user.cep or ''
        necessidade.bairro_servico = user.bairro or ''
        necessidade.endereco_servico = user.endereco or ''
        
        # Copiar coordenadas se existirem
        if hasattr(user, 'lat') and hasattr(user, 'lon'):
            necessidade.lat_servico = user.lat
            necessidade.lon_servico = user.lon
        
        necessidade.save()
        updated_count += 1
    
    print(f"✅ Atualizadas {updated_count} necessidades com endereço do usuário")

def reverse_populate_endereco_servico(apps, schema_editor):
    """
    Função reversa - limpar campos de endereço do serviço
    """
    Necessidade = apps.get_model('ads', 'Necessidade')
    
    Necessidade.objects.all().update(
        usar_endereco_usuario=True,
        cidade_servico='',
        estado_servico='',
        cep_servico='',
        bairro_servico='',
        endereco_servico='',
        numero_servico='',
        complemento_servico='',
        lat_servico=None,
        lon_servico=None,
        endereco_completo_json=None
    )

class Migration(migrations.Migration):

    dependencies = [
        ('ads', '0012_necessidade_bairro_servico_necessidade_cep_servico_and_more'),
    ]

    operations = [
        migrations.RunPython(
            populate_existing_necessidades_with_user_address,
            reverse_populate_endereco_servico,
        ),
    ]