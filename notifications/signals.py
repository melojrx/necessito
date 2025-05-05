# notifications/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from ads.models import Necessidade
from budgets.models import Orcamento
from .models import Notification, NotificationType

@receiver(post_save, sender=Necessidade)
def notificar_criacao_anuncio(sender, instance, created, **kwargs):
    """
    Cria uma notificação quando um novo anúncio é criado
    """
    if created:
        user = instance.cliente
        # Criar notificação no sistema
        Notification.objects.create(
            user=user,
            message=f"<strong>Novo Anúncio Criado</strong><br>Seu anúncio <strong>{instance.titulo}</strong> foi criado com sucesso.",
            notification_type=NotificationType.NEW_AD,
            necessidade=instance
        )

@receiver(post_save, sender=Necessidade)
def notificar_finalizacao_anuncio(sender, instance, **kwargs):
    """
    Notifica quando um anúncio é finalizado
    """
    # Verificar se o status mudou para finalizado
    if instance.status == 'finalizado':
        # Notificar o dono do anúncio
        Notification.objects.create(
            user=instance.cliente,
            message=f"<strong>Anúncio Finalizado</strong><br>Seu anúncio <strong>{instance.titulo}</strong> foi marcado como finalizado.",
            notification_type=NotificationType.NEW_END_AD,
            necessidade=instance
        )

        # Notificar o fornecedor do orçamento aceito
        orcamento_aceito = instance.orcamentos.filter(status='aceito').first()
        if orcamento_aceito and orcamento_aceito.fornecedor:
            Notification.objects.create(
                user=orcamento_aceito.fornecedor,
                message=f"<strong>Anúncio Finalizado</strong><br>O anúncio <strong>{instance.titulo}</strong> que você está atendendo foi finalizado.",
                notification_type=NotificationType.NEW_END_AD,
                necessidade=instance
            )

@receiver(post_save, sender=Orcamento)
def notificar_novo_orcamento(sender, instance, created, **kwargs):
    """
    Notifica o dono do anúncio quando um novo orçamento é criado
    """
    if created:
        anuncio = instance.anuncio
        cliente = anuncio.cliente

        # Criar notificação no sistema
        Notification.objects.create(
            user=cliente,
            message=f"<strong>Novo Orçamento Recebido</strong><br>Você recebeu um novo orçamento para seu anúncio <strong>{anuncio.titulo}</strong>.",
            notification_type=NotificationType.NEW_BUDGET,
            necessidade=anuncio
        )

@receiver(post_save, sender=Orcamento)
def notificar_orcamento_aceito(sender, instance, **kwargs):
    """
    Notifica o fornecedor quando seu orçamento é aceito
    """
    # Verificar se o status mudou para aceito
    if instance.status == 'aceito':
        fornecedor = instance.fornecedor
        anuncio = instance.anuncio

        # Criar notificação no sistema
        Notification.objects.create(
            user=fornecedor,
            message=f"<strong>Orçamento Aceito</strong><br>Seu orçamento para o anúncio <strong>{anuncio.titulo}</strong> foi aceito pelo cliente.",
            notification_type=NotificationType.NEW_BUDGET,
            necessidade=anuncio
        )