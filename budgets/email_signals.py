# budgets/email_signals.py
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from django.db import transaction
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
            "Atenciosamente,\nIndicaai"
        )
        send_mail(
            subject=assunto,
            message=corpo,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[cliente.email],
            fail_silently=False
        )

@receiver(pre_save, sender=Orcamento)
def enviar_email_orcamento_aceito_pelo_cliente(sender, instance, **kwargs):
    """
    Envia e-mail quando um orçamento é aceito pelo cliente (aguardando confirmação do fornecedor),
    garantindo envio apenas quando houver transição de status.
    """
    # Somente para updates (não no create)
    if not instance.pk:
        return

    # Busca o valor anterior do status para detectar transição
    try:
        previous = Orcamento.objects.get(pk=instance.pk)
    except Orcamento.DoesNotExist:
        return

    mudou_para_aceito_pelo_cliente = (
        previous.status != 'aceito_pelo_cliente' and instance.status == 'aceito_pelo_cliente'
    )

    if mudou_para_aceito_pelo_cliente:
        fornecedor = instance.fornecedor
        anuncio = instance.anuncio

        assunto = "Orçamento aceito pelo cliente"
        corpo = (
            f"Olá, {fornecedor.first_name}!\n\n"
            f"Seu orçamento para o anúncio '{anuncio.titulo}' foi aceito pelo cliente e aguarda sua confirmação.\n"
            "Acesse a plataforma para mais detalhes e confirmar o atendimento.\n\n"
            "Atenciosamente,\nIndicaai"
        )

        # Garante que o e-mail será enviado somente após o commit da transação
        transaction.on_commit(lambda: send_mail(
            subject=assunto,
            message=corpo,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[fornecedor.email],
            fail_silently=False
        ))