from django.core.management.base import BaseCommand
from categories.models import Categoria, SubCategoria
import csv

class Command(BaseCommand):
    help = 'Importa categorias e subcategorias de arquivos CSV'
    
    def add_arguments(self, parser):
        parser.add_argument('categorias_file', type=str)
        parser.add_argument('subcategorias_file', type=str)

    def handle(self, *args, **kwargs):
        # Importar Categorias
        categoria_map = {}
        with open(kwargs['categorias_file'], 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                categoria, created = Categoria.objects.get_or_create(
                    nome=row['nome']
                )
                categoria_map[row['id']] = categoria
                self.stdout.write(f'Categoria criada: {categoria.nome}')

        # Importar Subcategorias
        with open(kwargs['subcategorias_file'], 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                categoria_pai = categoria_map.get(row['categoria_id'])
                if not categoria_pai:
                    self.stderr.write(f'Erro: Categoria ID {row["categoria_id"]} não encontrada')
                    continue
                
                SubCategoria.objects.get_or_create(
                    categoria=categoria_pai,
                    nome=row['nome']
                )
                self.stdout.write(f'Subcategoria criada: {row["nome"]} → {categoria_pai.nome}')

        self.stdout.write(self.style.SUCCESS('✅ Importação concluída!'))