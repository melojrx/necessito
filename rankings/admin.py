from django.contrib import admin
from .models import Avaliacao, AvaliacaoCriterio


class AvaliacaoCriterioInline(admin.TabularInline):
    model = AvaliacaoCriterio
    extra = 1  # Número de formulários vazios a serem exibidos
    min_num = 1  # Número mínimo de formulários


@admin.register(Avaliacao)
class AvaliacaoAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'avaliado', 'anuncio', 'tipo_avaliacao', 'media_estrelas', 'data_avaliacao')
    list_filter = ('usuario', 'avaliado', 'anuncio', 'tipo_avaliacao', 'data_avaliacao')
    search_fields = ('usuario__username', 'avaliado__username', 'anuncio__titulo', 'tipo_avaliacao')
    inlines = [AvaliacaoCriterioInline]


@admin.register(AvaliacaoCriterio)
class AvaliacaoCriterioAdmin(admin.ModelAdmin):
    list_display = ('avaliacao', 'criterio', 'estrelas')
    list_filter = ('criterio', 'estrelas')
    search_fields = ('avaliacao__usuario__username', 'avaliacao__avaliado__username', 'criterio')
