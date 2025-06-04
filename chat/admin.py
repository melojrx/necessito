# chat/admin.py

from django.contrib import admin
from .models import ChatRoom, ChatMessage

@admin.register(ChatRoom)
class ChatRoomAdmin(admin.ModelAdmin):
    list_display = [
        'necessidade', 
        'cliente', 
        'fornecedor', 
        'total_mensagens',
        'criado_em', 
        'ativo'
    ]
    list_filter = ['ativo', 'criado_em', 'necessidade__categoria']
    search_fields = [
        'necessidade__titulo', 
        'cliente__first_name', 
        'cliente__last_name',
        'fornecedor__first_name', 
        'fornecedor__last_name'
    ]
    readonly_fields = ['criado_em']
    raw_id_fields = ['necessidade', 'cliente', 'fornecedor', 'orcamento']

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = [
        'chat_room', 
        'remetente', 
        'conteudo_resumido', 
        'data_envio', 
        'lida',
        'tem_anexo'
    ]
    list_filter = ['lida', 'data_envio', 'tipo_arquivo']
    search_fields = ['conteudo', 'remetente__first_name', 'remetente__last_name']
    readonly_fields = ['data_envio']
    
    def conteudo_resumido(self, obj):
        return obj.conteudo[:50] + "..." if len(obj.conteudo) > 50 else obj.conteudo
    conteudo_resumido.short_description = 'Conteúdo'
    
    def tem_anexo(self, obj):
        return bool(obj.arquivo_anexo)
    tem_anexo.boolean = True
    tem_anexo.short_description = 'Anexo'
