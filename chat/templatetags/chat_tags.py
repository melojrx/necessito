# chat/templatetags/chat_tags.py

from django import template
from ..utils import get_unread_messages_count, get_chat_stats

register = template.Library()

@register.simple_tag
def unread_messages_count(user):
    """Retorna número de mensagens não lidas"""
    if user.is_authenticated:
        return get_unread_messages_count(user)
    return 0

@register.simple_tag
def chat_stats(user):
    """Retorna estatísticas dos chats"""
    if user.is_authenticated:
        return get_chat_stats(user)
    return {}

@register.filter
def is_chat_participant(chat_room, user):
    """Verifica se usuário participa do chat"""
    return user in [chat_room.cliente, chat_room.fornecedor]

@register.filter
def format_file_size(size_bytes):
    """Formatar tamanho do arquivo"""
    if size_bytes == 0:
        return "0 B"
    size_names = ["B", "KB", "MB", "GB"]
    import math
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return f"{s} {size_names[i]}"