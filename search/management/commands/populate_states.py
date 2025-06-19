from django.core.management.base import BaseCommand
from search.models import State

class Command(BaseCommand):
    help = 'Popula a tabela State com todos os estados brasileiros'

    def handle(self, *args, **options):
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

        estados_criados = 0
        estados_existentes = 0

        for nome, sigla in estados_brasileiros:
            state, created = State.objects.get_or_create(
                abbreviation=sigla,
                defaults={'name': nome}
            )
            
            if created:
                estados_criados += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Estado criado: {nome} ({sigla})')
                )
            else:
                estados_existentes += 1
                self.stdout.write(
                    self.style.WARNING(f'• Estado já existe: {nome} ({sigla})')
                )

        self.stdout.write('\n' + '='*50)
        self.stdout.write(
            self.style.SUCCESS(
                f'✅ Processo concluído!\n'
                f'📊 Estados criados: {estados_criados}\n'
                f'📋 Estados já existentes: {estados_existentes}\n'
                f'🗂️ Total de estados: {State.objects.count()}'
            )
        ) 