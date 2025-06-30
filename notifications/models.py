from django.db import models
from ads.models import Necessidade
from core import settings

class NotificationType(models.TextChoices):
    NEW_AD = 'NEW_AD', 'Novo Anúncio'
    NEW_END_AD = 'NEW_END_AD', 'Anúncio Finalizado'
    NEW_BUDGET = 'NEW_BUDGET', 'Novo Orçamento'
    BUDGET_REJECTED = 'BUDGET_REJECTED', 'Orçamento Rejeitado'
    NEW_AVALIACAO = 'NEW_AVALIACAO', 'Nova Avaliação'
    NEW_CHAT_MESSAGE = 'NEW_CHAT_MESSAGE', 'Nova Mensagem no Chat'

class Notification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    notification_type = models.CharField(
        max_length=20,
        choices=NotificationType.choices,
        default=NotificationType.NEW_AD
    )
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    necessidade = models.ForeignKey('ads.Necessidade', on_delete=models.CASCADE, null=True, blank=True)
    chat_room = models.ForeignKey('chat.ChatRoom', on_delete=models.CASCADE, null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Notificação para {self.user.email} em {self.created_at}"

