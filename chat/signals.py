from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import ChatMessage
from notifications.models import Notification, NotificationType

User = get_user_model()

@receiver(post_save, sender=ChatMessage)
def notificar_nova_mensagem_chat(sender, instance, created, **kwargs):
    """
    Cria notificação quando uma nova mensagem de chat é recebida
    """
    if created:
        chat_room = instance.chat_room
        remetente = instance.remetente
        
        # Determinar quem deve receber a notificação (o outro usuário)
        if remetente == chat_room.cliente:
            destinatario = chat_room.fornecedor
            papel_remetente = "cliente"
        else:
            destinatario = chat_room.cliente
            papel_remetente = "fornecedor"
        
        # Truncar mensagem se for muito longa
        conteudo_resumido = instance.conteudo[:100] + "..." if len(instance.conteudo) > 100 else instance.conteudo
        
        # Criar notificação
        Notification.objects.create(
            user=destinatario,
            message=(
                f"<strong>Nova Mensagem no Chat</strong><br>"
                f"<strong>{remetente.get_full_name()}</strong> ({papel_remetente}) enviou: <br>"
                f"<em>'{conteudo_resumido}'</em><br>"
                f"<small>Anúncio: {chat_room.necessidade.titulo}</small>"
            ),
            notification_type=NotificationType.NEW_CHAT_MESSAGE,
            necessidade=chat_room.necessidade
        )
        
        # Opcional: Enviar email se usuário estiver offline por muito tempo
        # Implementar lógica de email aqui se necessário 