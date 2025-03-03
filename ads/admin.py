from django.contrib import admin
from .models import Necessidade, AnuncioImagem


@admin.register(Necessidade)
class NecessidadeAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'cliente', 'categoria', 'status', 'data_criacao')
    list_filter = ('status', 'categoria')
    search_fields = ('titulo', 'descricao')

@admin.register(AnuncioImagem)
class AnuncioImagemAdmin(admin.ModelAdmin):
    list_display = ('anuncio', 'imagem', 'criado_em')
    list_filter = ('anuncio',)
    search_fields = ('anuncio',)
