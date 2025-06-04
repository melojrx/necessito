# chat/utils.py

from django.core.cache import cache
from django.db.models import Q, Count
from .models import ChatRoom, ChatMessage

def get_unread_messages_count(user):
    """Retorna número total de mensagens não lidas do usuário"""
    cache_key = f'unread_messages_{user.id}'
    count = cache.get(cache_key)
    
    if count is None:
        count = ChatMessage.objects.filter(
            chat_room__in=ChatRoom.objects.filter(
                Q(cliente=user) | Q(fornecedor=user),
                ativo=True
            ),
            lida=False
        ).exclude(remetente=user).count()
        
        # Cache por 60 segundos
        cache.set(cache_key, count, 60)
    
    return count

def invalidate_unread_cache(user):
    """Invalida o cache de mensagens não lidas"""
    cache.delete(f'unread_messages_{user.id}')

def get_chat_stats(user):
    """Retorna estatísticas dos chats do usuário"""
    chats = ChatRoom.objects.filter(
        Q(cliente=user) | Q(fornecedor=user),
        ativo=True
    )
    
    return {
        'total_chats': chats.count(),
        'chats_com_orcamento': chats.filter(orcamento__isnull=False).count(),
        'mensagens_enviadas': ChatMessage.objects.filter(
            chat_room__in=chats,
            remetente=user
        ).count(),
        'mensagens_nao_lidas': get_unread_messages_count(user)
    }