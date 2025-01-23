from django.contrib import admin
from django.utils.html import format_html
from .models import Categoria, SubCategoria

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'criado_em', 'modificado_em')
    search_fields = ('nome',)
    readonly_fields = ('imagem_preview',)

    def imagem_preview(self, obj):
        if obj.imagem():
            return format_html(f'<img src="{obj.imagem()}" style="max-height: 100px;" />')
        return "Sem imagem"
    imagem_preview.short_description = "Imagem"

@admin.register(SubCategoria)
class SubCategoriaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'categoria', 'criado_em', 'modificado_em')
    search_fields = ('nome', 'categoria__nome')

