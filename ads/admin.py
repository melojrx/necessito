from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import Necessidade, AnuncioImagem, Disputa


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


@admin.register(Disputa)
class DisputaAdmin(admin.ModelAdmin):
    """Interface administrativa para disputas com funcionalidades avançadas."""
    
    list_display = [
        'id',
        'necessidade_link',
        'usuario_abertura',
        'get_tipo_usuario',
        'status_badge',
        'get_dias_em_aberto',
        'data_abertura',
        'precisa_atencao_admin'
    ]
    
    list_filter = [
        'status',
        'data_abertura',
        'data_resolucao',
        ('resolvida_por', admin.RelatedOnlyFieldListFilter),
    ]
    
    search_fields = [
        'necessidade__titulo',
        'usuario_abertura__first_name',
        'usuario_abertura__last_name',
        'usuario_abertura__email',
        'motivo',
        'resolucao'
    ]
    
    readonly_fields = [
        'necessidade',
        'orcamento',
        'usuario_abertura',
        'data_abertura',
        'data_modificacao',
        'ip_usuario_abertura',
        'get_contraparte_display',
        'get_orcamento_details',
        'get_necessidade_details'
    ]
    
    fieldsets = [
        ('Informações Básicas', {
            'fields': [
                'necessidade',
                'get_necessidade_details',
                'orcamento',
                'get_orcamento_details',
            ]
        }),
        ('Disputante', {
            'fields': [
                'usuario_abertura',
                'get_contraparte_display',
                'ip_usuario_abertura',
                'data_abertura',
            ]
        }),
        ('Detalhes da Disputa', {
            'fields': [
                'motivo',
                'arquivo_evidencia',
            ]
        }),
        ('Resolução (Admin)', {
            'fields': [
                'status',
                'resolucao',
                'status_final_necessidade',
                'resolvida_por',
                'data_resolucao',
                'comentarios_internos',
            ]
        }),
        ('Metadata', {
            'fields': [
                'data_modificacao',
            ],
            'classes': ['collapse']
        }),
    ]
    
    actions = [
        'marcar_em_analise',
        'exportar_disputas_csv',
    ]
    
    def necessidade_link(self, obj):
        """Link para a necessidade."""
        url = reverse('admin:ads_necessidade_change', args=[obj.necessidade.pk])
        return format_html('<a href="{}">{}</a>', url, obj.necessidade.titulo)
    necessidade_link.short_description = 'Necessidade'
    
    def status_badge(self, obj):
        """Badge colorido para status."""
        colors = {
            'aberta': '#dc3545',      # Vermelho
            'em_analise': '#ffc107',  # Amarelo
            'resolvida': '#28a745',   # Verde
            'cancelada': '#6c757d',   # Cinza
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 6px; border-radius: 3px; font-size: 11px;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def get_tipo_usuario(self, obj):
        """Tipo do usuário que abriu (cliente/fornecedor)."""
        tipo = obj.get_tipo_usuario_abertura()
        colors = {
            'cliente': '#007bff',
            'fornecedor': '#17a2b8',
        }
        color = colors.get(tipo, '#6c757d')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            tipo.title()
        )
    get_tipo_usuario.short_description = 'Tipo'
    
    def get_dias_em_aberto(self, obj):
        """Dias em aberto com indicador visual."""
        dias = obj.get_dias_em_aberto()
        if dias > 3:
            color = '#dc3545'  # Vermelho para urgente
        elif dias > 1:
            color = '#ffc107'  # Amarelo para atenção
        else:
            color = '#28a745'  # Verde para recente
        
        return format_html(
            '<span style="color: {}; font-weight: bold;">{} dias</span>',
            color,
            dias
        )
    get_dias_em_aberto.short_description = 'Dias em aberto'
    
    def precisa_atencao_admin(self, obj):
        """Indicador se precisa atenção."""
        if obj.precisa_atencao_admin:
            return format_html(
                '<span style="color: #dc3545; font-weight: bold;">⚠️ URGENTE</span>'
            )
        return ''
    precisa_atencao_admin.short_description = 'Atenção'
    
    def get_contraparte_display(self, obj):
        """Exibe informações da contraparte."""
        contraparte = obj.get_contraparte(obj.usuario_abertura)
        if contraparte:
            return f"{contraparte.get_full_name()} ({contraparte.email})"
        return "N/A"
    get_contraparte_display.short_description = 'Contraparte'
    
    def get_orcamento_details(self, obj):
        """Detalhes do orçamento."""
        orc = obj.orcamento
        return format_html(
            '<strong>Fornecedor:</strong> {}<br>'
            '<strong>Valor:</strong> R$ {:.2f}<br>'
            '<strong>Status:</strong> {}',
            orc.fornecedor.get_full_name(),
            orc.get_total_geral(),
            orc.get_status_display()
        )
    get_orcamento_details.short_description = 'Detalhes do Orçamento'
    
    def get_necessidade_details(self, obj):
        """Detalhes da necessidade."""
        nec = obj.necessidade
        return format_html(
            '<strong>Cliente:</strong> {}<br>'
            '<strong>Status:</strong> {}<br>'
            '<strong>Categoria:</strong> {}',
            nec.cliente.get_full_name(),
            nec.get_status_display(),
            nec.categoria.nome
        )
    get_necessidade_details.short_description = 'Detalhes da Necessidade'
    
    # Actions customizadas
    def marcar_em_analise(self, request, queryset):
        """Marcar disputas selecionadas como em análise."""
        updated = queryset.filter(status='aberta').update(status='em_analise')
        self.message_user(
            request,
            f'{updated} disputa(s) marcada(s) como em análise.'
        )
    marcar_em_analise.short_description = 'Marcar como em análise'
    
    def exportar_disputas_csv(self, request, queryset):
        """Exportar disputas selecionadas para CSV."""
        import csv
        from django.http import HttpResponse
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="disputas.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'ID', 'Necessidade', 'Cliente', 'Fornecedor', 'Status',
            'Data Abertura', 'Dias em Aberto', 'Motivo'
        ])
        
        for disputa in queryset:
            writer.writerow([
                disputa.id,
                disputa.necessidade.titulo,
                disputa.necessidade.cliente.get_full_name(),
                disputa.orcamento.fornecedor.get_full_name(),
                disputa.get_status_display(),
                disputa.data_abertura.strftime('%d/%m/%Y %H:%M'),
                disputa.get_dias_em_aberto(),
                disputa.motivo[:100] + '...' if len(disputa.motivo) > 100 else disputa.motivo
            ])
        
        return response
    exportar_disputas_csv.short_description = 'Exportar para CSV'
    
    def get_queryset(self, request):
        """Otimizar queries."""
        return super().get_queryset(request).select_related(
            'necessidade',
            'necessidade__cliente',
            'necessidade__categoria',
            'orcamento',
            'orcamento__fornecedor',
            'usuario_abertura',
            'resolvida_por'
        )
    
    def save_model(self, request, obj, form, change):
        """Definir quem resolveu a disputa."""
        if change and obj.status == 'resolvida' and not obj.resolvida_por:
            obj.resolvida_por = request.user
        super().save_model(request, obj, form, change)
    
    # Customizar aparência
    class Media:
        css = {
            'all': ('admin/css/disputas.css',)
        }
        js = ('admin/js/disputas.js',)
