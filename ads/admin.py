from django.contrib import admin
from .models import Necessidade


@admin.register(Necessidade)
class NecessidadeAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'cliente', 'categoria', 'status', 'data_criacao')
    list_filter = ('status', 'categoria')
    search_fields = ('titulo', 'descricao')
