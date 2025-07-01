# notifications/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
from ads.models import Necessidade
from notifications.models import Notification, NotificationType
from budgets.models import Orcamento
from rankings.models import Avaliacao
from notifications.utils import send_notification_email, get_anuncio_url, get_perfil_url, get_avaliacao_url

@receiver(post_save, sender=Necessidade)
def notificar_criacao_anuncio(sender, instance, created, **kwargs):
    """
    Cria uma notificação e envia e-mail quando um novo anúncio é criado
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
        
        # Enviar e-mail profissional
        context = {
            'user': user,
            'anuncio': instance,
            'anuncio_url': get_anuncio_url(instance),
        }
        
        send_notification_email(
            template_name='anuncio_criado',
            subject='🎯 Anúncio criado com sucesso!',
            recipient_email=user.email,
            context=context
        )

@receiver(post_save, sender=Necessidade)
def notificar_finalizacao_anuncio(sender, instance, **kwargs):
    if instance.status == 'finalizado':
        orcamento_aceito = instance.orcamentos.filter(status='aceito').first()
        
        # Notifica cliente
        Notification.objects.create(
            user=instance.cliente,
            message=f"<strong>Anúncio Finalizado</strong><br>Seu anúncio '{instance.titulo}' foi finalizado.",
            notification_type=NotificationType.NEW_END_AD,
            necessidade=instance
        )
        
        # Envia e-mail para cliente
        context_cliente = {
            'user': instance.cliente,
            'anuncio': instance,
            'orcamento_aceito': orcamento_aceito,
            'avaliacao_url': get_avaliacao_url(instance) if orcamento_aceito else None,
        }
        
        send_notification_email(
            template_name='anuncio_finalizado',
            subject='✅ Projeto finalizado com sucesso!',
            recipient_email=instance.cliente.email,
            context=context_cliente
        )

        # Notifica fornecedor (caso exista orçamento aceito)
        if orcamento_aceito:
            Notification.objects.create(
                user=orcamento_aceito.fornecedor,
                message=f"<strong>Anúncio Finalizado</strong><br>O anúncio '{instance.titulo}' que você atendeu foi finalizado.",
                notification_type=NotificationType.NEW_END_AD,
                necessidade=instance
            )

            # Envia e-mail para fornecedor
            context_fornecedor = {
                'user': orcamento_aceito.fornecedor,
                'anuncio': instance,
                'orcamento_aceito': orcamento_aceito,
            }
            
            send_notification_email(
                template_name='anuncio_finalizado',
                subject='🎯 Projeto concluído!',
                recipient_email=orcamento_aceito.fornecedor.email,
                context=context_fornecedor
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
        
        # Enviar e-mail profissional
        context = {
            'user': cliente,
            'anuncio': anuncio,
            'orcamento': instance,
            'anuncio_url': get_anuncio_url(anuncio),
        }
        
        send_notification_email(
            template_name='orcamento_recebido',
            subject='💰 Novo orçamento recebido!',
            recipient_email=cliente.email,
            context=context
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
        
        # Enviar e-mail profissional
        context = {
            'user': fornecedor,
            'anuncio': anuncio,
            'orcamento': instance,
            'anuncio_url': get_anuncio_url(anuncio),
        }
        
        send_notification_email(
            template_name='orcamento_aceito',
            subject='🎉 Parabéns! Seu orçamento foi aceito!',
            recipient_email=fornecedor.email,
            context=context
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

        # Enviar e-mail profissional
        context = {
            'user': fornecedor,
            'anuncio': anuncio,
            'orcamento': instance,
        }
        
        send_notification_email(
            template_name='orcamento_rejeitado',
            subject='📋 Atualização sobre sua proposta',
            recipient_email=fornecedor.email,
            context=context
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

        # Enviar e-mail profissional
        context = {
            'user': avaliado,
            'anuncio': anuncio,
            'avaliacao': instance,
            'perfil_url': get_perfil_url(avaliado),
        }
        
        send_notification_email(
            template_name='nova_avaliacao',
            subject='⭐ Nova avaliação recebida!',
            recipient_email=avaliado.email,
            context=context
        )