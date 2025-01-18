from django.contrib import admin
from .models import Categoria, SubCategoria

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'criado_em', 'modificado_em')
    search_fields = ('nome',)

@admin.register(SubCategoria)
class SubCategoriaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'categoria', 'criado_em', 'modificado_em')
    search_fields = ('nome', 'categoria__nome')

