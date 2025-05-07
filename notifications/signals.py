# notifications/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from ads.models import Necessidade
from notifications.models import Notification, NotificationType
from budgets.models import Orcamento
from rankings.models import Avaliacao

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
    if instance.status == 'finalizado':
        # Notifica cliente
        Notification.objects.create(
            user=instance.cliente,
            message=f"<strong>Anúncio Finalizado</strong><br>Seu anúncio '{instance.titulo}' foi finalizado.",
            notification_type=NotificationType.NEW_END_AD,
            necessidade=instance
        )

        # Notifica fornecedor (caso exista orçamento aceito)
        orcamento_aceito = instance.orcamentos.filter(status='aceito').first()
        if orcamento_aceito:
            Notification.objects.create(
                user=orcamento_aceito.fornecedor,
                message=f"<strong>Anúncio Finalizado</strong><br>O anúncio '{instance.titulo}' que você atendeu foi finalizado.",
                notification_type=NotificationType.NEW_END_AD,
                necessidade=instance
            )

            # Envia email para fornecedor
            send_mail(
                subject="Anúncio Finalizado",
                message=f"Olá {orcamento_aceito.fornecedor.first_name},\n\nO anúncio '{instance.titulo}' que você atendeu foi finalizado pelo cliente.\n\nAtenciosamente,\nNecessito",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[orcamento_aceito.fornecedor.email],
                fail_silently=False
            )

        # Envia email para cliente
        send_mail(
            subject="Anúncio Finalizado",
            message=f"Olá {instance.cliente.first_name},\n\nSeu anúncio '{instance.titulo}' foi finalizado com sucesso.\n\nObrigado por usar nossa plataforma.\n\nAtenciosamente,\nNecessito",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[instance.cliente.email],
            fail_silently=False
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

@receiver(post_save, sender=Orcamento)
def notificar_orcamento_rejeitado(sender, instance, **kwargs):
    """
    Notifica o fornecedor quando o orçamento for rejeitado
    """
    if instance.status == 'rejeitado':
        fornecedor = instance.fornecedor
        anuncio = instance.anuncio

        # Criar notificação interna
        Notification.objects.create(
            user=fornecedor,
            message=(
                f"<strong>Orçamento Rejeitado</strong><br>"
                f"O cliente rejeitou seu orçamento para o anúncio <strong>{anuncio.titulo}</strong>."
            ),
            notification_type=NotificationType.BUDGET_REJECTED,
            necessidade=anuncio
        )

        # Enviar email
        assunto = "Orçamento Rejeitado"
        corpo = (
            f"Olá, {fornecedor.first_name}!\n\n"
            f"O cliente rejeitou seu orçamento enviado para o anúncio '{anuncio.titulo}'.\n"
            "Acesse a plataforma para mais detalhes.\n\n"
            "Atenciosamente,\nNecessito"
        )
        send_mail(
            subject=assunto,
            message=corpo,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[fornecedor.email],
            fail_silently=False
        )

@receiver(post_save, sender=Avaliacao)
def notificar_nova_avaliacao(sender, instance, created, **kwargs):
    """
    Notifica o usuário avaliado que recebeu uma nova avaliação
    """
    if created:
        avaliado = instance.avaliado
        avaliador = instance.usuario
        anuncio = instance.anuncio

        # Criar notificação interna
        Notification.objects.create(
            user=avaliado,
            message=(
                f"<strong>Nova Avaliação Recebida</strong><br>"
                f"Você recebeu uma nova avaliação no anúncio <strong>{anuncio.titulo}</strong>."
            ),
            notification_type=NotificationType.NEW_AVALIACAO,
            necessidade=anuncio
        )

        # Enviar email
        assunto = "Nova Avaliação Recebida"
        corpo = (
            f"Olá, {avaliado.first_name}!\n\n"
            f"Você recebeu uma nova avaliação no anúncio '{anuncio.titulo}'.\n"
            "Acesse a plataforma para visualizar os detalhes.\n\n"
            "Atenciosamente,\nNecessito"
        )
        send_mail(
            subject=assunto,
            message=corpo,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[avaliado.email],
            fail_silently=False
        )