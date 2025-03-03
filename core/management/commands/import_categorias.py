import re
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

import django
django.setup()

from django.core.management.base import BaseCommand
from categories.models import Categoria, SubCategoria

class Command(BaseCommand):
    help = 'Importa categorias e subcategorias da construção civil de arquivo TXT'

    def add_arguments(self, parser):
        parser.add_argument(
            'arquivo',
            type=str,
            help='Caminho completo para o arquivo TXT'
        )

    def handle(self, *args, **kwargs):
        caminho = kwargs['arquivo']
        categoria_atual = None
        contador_subcategorias = 0

        with open(caminho, 'r', encoding='utf-8') as f:
            for linha in f:
                linha = linha.strip()
                
                # Detecta categoria (padrão: "1. Nome")
                if re.match(r'^\d+\. ', linha):
                    nome_categoria = re.sub(r'^\d+\.\s*', '', linha)
                    categoria_atual, criada = Categoria.objects.get_or_create(
                        nome=nome_categoria,
                        defaults={'descricao': f"Descrição para {nome_categoria}"}
                    )
                    contador_subcategorias = 0
                    status = "CRIADA" if criada else "EXISTENTE"
                    self.stdout.write(f"[{status}] Categoria: {nome_categoria}")
                
                # Detecta subcategorias (5 por categoria)
                elif linha and categoria_atual and contador_subcategorias < 5:
                    subcategoria, criada = SubCategoria.objects.get_or_create(
                        categoria=categoria_atual,
                        nome=linha,
                        defaults={'descricao': f"Descrição para {linha}"}
                    )
                    contador_subcategorias += 1
                    status = "CRIADA" if criada else "EXISTENTE"
                    self.stdout.write(f"  ↳ [{status}] Subcategoria: {linha}")

        self.stdout.write(self.style.SUCCESS(f'''
            \nResumo da Importação:
            Total de Categorias: {Categoria.objects.count()}
            Total de Subcategorias: {SubCategoria.objects.count()}
        '''))