import json
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from datetime import datetime

User = get_user_model()

class Command(BaseCommand):
    help = 'Importa usuários de um arquivo JSON simplificado'

    def add_arguments(self, parser):
        parser.add_argument('arquivo_json', type=str, help='Caminho do arquivo JSON')

    def handle(self, *args, **kwargs):
        arquivo_json = kwargs['arquivo_json']

        try:
            with open(arquivo_json, encoding='utf-8') as f:
                usuarios = json.load(f)

            for usuario in usuarios:
                email = usuario['email']
                if User.objects.filter(email=email).exists():
                    self.stdout.write(self.style.WARNING(f"Usuário {email} já existe. Pulando..."))
                    continue

                nome_completo = usuario['nome'].split()
                first_name = nome_completo[0]
                last_name = ' '.join(nome_completo[1:]) if len(nome_completo) > 1 else ''

                user = User(
                    email=email,
                    first_name=first_name,
                    last_name=last_name,
                    telefone=usuario.get('celular', ''),
                    endereco=usuario.get('endereco', ''),
                    bairro=usuario.get('bairro', ''),
                    cep=usuario.get('cep', ''),
                    cidade=usuario.get('cidade', ''),
                    estado=usuario.get('estado', '').upper(),
                    cpf=usuario.get('cpf', ''),
                    data_nascimento=datetime.strptime(usuario['data_nasc'], "%d/%m/%Y").date(),
                    is_client=True
                )
                user.set_password(usuario['senha'])
                user.save()

                self.stdout.write(self.style.SUCCESS(f"Usuário {email} importado com sucesso!"))

        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Erro: {e}"))
