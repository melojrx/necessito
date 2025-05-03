from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
import requests
import time

User = get_user_model()

class Command(BaseCommand):
    help = 'Geolocaliza e atualiza os campos lat/lon dos usuários sem coordenadas.'

    def handle(self, *args, **kwargs):
        usuarios = User.objects.filter(lat__isnull=True, lon__isnull=True).exclude(cidade='').exclude(estado='')

        total = usuarios.count()
        self.stdout.write(f"Encontrados {total} usuários sem coordenadas.")

        for idx, user in enumerate(usuarios, start=1):
            endereco = f"{user.cidade}, {user.estado}, Brasil"
            self.stdout.write(f"[{idx}/{total}] Geocodificando: {endereco}")

            try:
                resp = requests.get(
                    'https://nominatim.openstreetmap.org/search',
                    params={'q': endereco, 'format': 'json'},
                    headers={'User-Agent': 'seu-app/1.0'}
                )
                data = resp.json()
                if data:
                    user.lat = float(data[0]['lat'])
                    user.lon = float(data[0]['lon'])
                    user.save(update_fields=['lat', 'lon'])
                    self.stdout.write(f"✔️ Atualizado: {user.email} → lat={user.lat}, lon={user.lon}")
                else:
                    self.stdout.write(f"⚠️ Nominatim não retornou resultado para {endereco}")

            except Exception as e:
                self.stdout.write(f"❌ Erro ao geocodificar {endereco}: {e}")

            time.sleep(1)  # Respeitar limite de 1 requisição/segundo do Nominatim

        self.stdout.write("✅ Finalizado.")
