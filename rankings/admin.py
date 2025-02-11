from django.contrib import admin
from .models import Avaliacao


@admin.register(Avaliacao)
class AvaliacaoAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'avaliado', 'anuncio', 'tipo_avaliacao', 'estrelas', 'data_avaliacao')
    list_filter = ('usuario', 'avaliado', 'anuncio', 'tipo_avaliacao', 'estrelas', 'data_avaliacao')
    search_fields = ('usuario', 'avaliado', 'anuncio', 'tipo_avaliacao', 'estrelas', 'data_avaliacao')