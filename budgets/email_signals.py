# budgets/email_signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from .models import Orcamento

@receiver(post_save, sender=Orcamento)
def enviar_email_novo_orcamento(sender, instance, created, **kwargs):
    """
    Envia e-mail quando um novo orçamento é criado
    """
    if created:
        anuncio = instance.anuncio
        cliente = anuncio.cliente

        # Enviar e-mail
        assunto = "Novo Orçamento Recebido"
        corpo = (
            f"Olá, {cliente.first_name}!\n\n"
            f"Você recebeu um novo orçamento para seu anúncio '{anuncio.titulo}'.\n"
            "Acesse a plataforma para visualizar os detalhes e responder.\n\n"
            "Atenciosamente,\nNecessito"
        )
        send_mail(
            subject=assunto,
            message=corpo,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[cliente.email],
            fail_silently=False
        )

@receiver(post_save, sender=Orcamento)
def enviar_email_orcamento_aceito(sender, instance, **kwargs):
    """
    Envia e-mail quando um orçamento é aceito
    """
    # Verificar se o status mudou para aceito
    if instance.status == 'aceito':
        fornecedor = instance.fornecedor
        anuncio = instance.anuncio

        # Enviar e-mail
        assunto = "Orçamento Aceito"
        corpo = (
            f"Olá, {fornecedor.first_name}!\n\n"
            f"Seu orçamento para o anúncio '{anuncio.titulo}' foi aceito pelo cliente.\n"
            "Acesse a plataforma para mais detalhes e iniciar o atendimento.\n\n"
            "Atenciosamente,\nNecessito"
        )
        send_mail(
            subject=assunto,
            message=corpo,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[fornecedor.email],
            fail_silently=False
        )