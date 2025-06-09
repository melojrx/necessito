from django.contrib import admin
from .models import Orcamento, OrcamentoItem


class OrcamentoItemInline(admin.TabularInline):
    model = OrcamentoItem
    extra = 0
    fields = [
        'tipo', 'descricao', 'quantidade', 'unidade', 'valor_unitario',
        'ncm', 'icms_percentual', 'ipi_percentual', 'st_percentual', 'difal_percentual',
        'cnae', 'aliquota_iss'
    ]
    readonly_fields = []

    def get_fields(self, request, obj=None):
        fields = [
            'tipo', 'descricao', 'quantidade', 'unidade', 'valor_unitario'
        ]
        
        # Adicionar campos específicos baseado no contexto
        fields.extend([
            'ncm', 'icms_percentual', 'ipi_percentual', 'st_percentual', 'difal_percentual',
            'cnae', 'aliquota_iss'
        ])
        
        return fields


@admin.register(Orcamento)
class OrcamentoAdmin(admin.ModelAdmin):
    inlines = [OrcamentoItemInline]
    list_display = (
        'id', 'fornecedor', 'anuncio', 'valor_total_com_impostos', 
        'status', 'prazo_validade', 'prazo_entrega', 'data_criacao'
    )
    list_filter = ('status', 'prazo_validade', 'prazo_entrega', 'data_criacao')
    search_fields = ('fornecedor__first_name', 'fornecedor__last_name', 'anuncio__titulo')
    readonly_fields = ('data_criacao', 'modificado_em', 'valor_total', 'valor_total_com_impostos')
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('fornecedor', 'anuncio', 'status')
        }),
        ('Prazos', {
            'fields': ('prazo_validade', 'prazo_entrega')
        }),
        ('Observações e Anexos', {
            'fields': ('observacao', 'arquivo_anexo')
        }),
        ('Valores', {
            'fields': ('valor_total', 'valor_total_com_impostos'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('data_criacao', 'modificado_em'),
            'classes': ('collapse',)
        }),
    )

    def valor_total_com_impostos(self, obj):
        """Método para exibir o valor total com impostos no admin"""
        return f"R$ {obj.valor_total_com_impostos():,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
    
    valor_total_com_impostos.short_description = 'Valor Total (c/ impostos)'


@admin.register(OrcamentoItem)
class OrcamentoItemAdmin(admin.ModelAdmin):
    list_display = (
        'orcamento', 'tipo', 'descricao', 'quantidade', 'unidade', 
        'valor_unitario', 'total', 'ncm', 'cnae'
    )
    list_filter = ('tipo', 'orcamento__status')
    search_fields = ('descricao', 'ncm', 'cnae', 'orcamento__fornecedor__first_name')
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('orcamento', 'tipo', 'descricao', 'quantidade', 'unidade', 'valor_unitario')
        }),
        ('Campos de Material', {
            'fields': ('ncm', 'icms_percentual', 'ipi_percentual', 'st_percentual', 'difal_percentual'),
            'classes': ('collapse',),
            'description': 'Campos específicos para materiais'
        }),
        ('Campos de Serviço', {
            'fields': ('cnae', 'aliquota_iss'),
            'classes': ('collapse',),
            'description': 'Campos específicos para serviços'
        }),
    )

    def total(self, obj):
        """Método para exibir o total do item no admin"""
        return f"R$ {obj.total:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
    
    total.short_description = 'Total (c/ impostos)'