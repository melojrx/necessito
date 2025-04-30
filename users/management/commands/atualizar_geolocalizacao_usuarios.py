import requests
from django.core.management.base import BaseCommand
from users.models import User

class Command(BaseCommand):
    help = "Atualiza latitude e longitude dos usuários com base no CEP"

    def handle(self, *args, **options):
        usuarios = User.objects.filter(cep__isnull=False).exclude(cep="").filter(lat__isnull=True, lon__isnull=True)
        total = usuarios.count()

        self.stdout.write(f"Atualizando geolocalização de {total} usuários...")

        for user in usuarios:
            cep = user.cep.replace("-", "").strip()
            response = requests.get(f"https://nominatim.openstreetmap.org/search?format=json&q={cep}", headers={"User-Agent": "DjangoApp"})
            if response.status_code == 200:
                data = response.json()
                if data:
                    user.lat = float(data[0]['lat'])
                    user.lon = float(data[0]['lon'])
                    user.save()
                    self.stdout.write(self.style.SUCCESS(f"✓ {user.email} atualizado com sucesso."))
                else:
                    self.stdout.write(self.style.WARNING(f"✗ CEP não encontrado para {user.email}"))
            else:
                self.stdout.write(self.style.ERROR(f"✗ Erro na API para {user.email}"))