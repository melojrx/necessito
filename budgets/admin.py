from django.contrib import admin
from .models import Orcamento


@admin.register(Orcamento)
class OrcamentoAdmin(admin.ModelAdmin):
    list_display = ('fornecedor', 'anuncio', 'descricao', 'quantidade', 'unidade', 'valor', 'prazo_validade', 'prazo_entrega', 'arquivo_anexo', 'observacao', )
    list_filter = ('fornecedor', 'anuncio', 'status', 'prazo_validade', 'prazo_entrega', )
    search_fields = ('fornecedor', 'anuncio', 'status', 'prazo_validade', 'prazo_entrega', )