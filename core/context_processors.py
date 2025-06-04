from notifications.models import Notification

def unread_notifications(request):
    if request.user.is_authenticated:
        count = Notification.objects.filter(user=request.user, is_read=False).count()
    else:
        count = 0
    return {
        'unread_notifications_count': count
    }

def unread_messages(request):
    """Context processor para contar mensagens não lidas do chat"""
    if request.user.is_authenticated:
        try:
            # Importar aqui para evitar problemas de dependência circular
            from django.db.models import Q
            from chat.models import ChatRoom, ChatMessage
            
            count = ChatMessage.objects.filter(
                chat_room__in=ChatRoom.objects.filter(
                    Q(cliente=request.user) | Q(fornecedor=request.user),
                    ativo=True
                ),
                lida=False
            ).exclude(remetente=request.user).count()
        except Exception:
            # Se houver qualquer erro, retornar 0
            count = 0
    else:
        count = 0
    
    return {
        'unread_messages_count': count
    }
