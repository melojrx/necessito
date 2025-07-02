import os
from django.core.management.base import BaseCommand
from django.conf import settings
from django.core.files.base import ContentFile
from ads.models import Necessidade, AnuncioImagem


class Command(BaseCommand):
    help = 'Adiciona imagem padrão do Indicaai aos anúncios que não possuem imagens'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Apenas mostra quais anúncios seriam afetados, sem fazer alterações',
        )

    def handle(self, *args, **options):
        # Buscar anúncios sem imagens
        anuncios_sem_imagem = Necessidade.objects.filter(imagens__isnull=True).distinct()
        
        self.stdout.write(f'Encontrados {anuncios_sem_imagem.count()} anúncios sem imagem')
        
        if options['dry_run']:
            self.stdout.write('=== MODO DRY RUN - Nenhuma alteração será feita ===')
            for anuncio in anuncios_sem_imagem:
                self.stdout.write(f'ID: {anuncio.id} - {anuncio.titulo}')
            return
        
        # Caminho para a imagem padrão
        imagem_padrao_path = os.path.join(settings.STATIC_ROOT or 'static', 'img', 'logo_Indicaai_anuncio.png')
        
        # Se STATIC_ROOT não estiver definido, usar o diretório static local
        if not os.path.exists(imagem_padrao_path):
            imagem_padrao_path = os.path.join(settings.BASE_DIR, 'static', 'img', 'logo_Indicaai_anuncio.png')
        
        if not os.path.exists(imagem_padrao_path):
            self.stdout.write(
                self.style.ERROR(f'Imagem padrão não encontrada em: {imagem_padrao_path}')
            )
            return
        
        # Ler o conteúdo da imagem padrão
        try:
            with open(imagem_padrao_path, 'rb') as f:
                imagem_content = f.read()
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Erro ao ler imagem padrão: {e}')
            )
            return
        
        contador_sucesso = 0
        contador_erro = 0
        
        for anuncio in anuncios_sem_imagem:
            try:
                # Criar uma instância AnuncioImagem com a imagem padrão
                imagem_padrao = AnuncioImagem(anuncio=anuncio)
                imagem_padrao.imagem.save(
                    f'anuncio_{anuncio.id}_padrao.png',
                    ContentFile(imagem_content),
                    save=True
                )
                
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Imagem adicionada ao anúncio ID: {anuncio.id} - {anuncio.titulo}')
                )
                contador_sucesso += 1
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'✗ Erro ao adicionar imagem ao anúncio ID: {anuncio.id} - {e}')
                )
                contador_erro += 1
        
        self.stdout.write('')
        self.stdout.write(f'=== RESUMO ===')
        self.stdout.write(f'Anúncios processados com sucesso: {contador_sucesso}')
        self.stdout.write(f'Anúncios com erro: {contador_erro}')
        self.stdout.write(f'Total: {contador_sucesso + contador_erro}') 