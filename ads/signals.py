# ads/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from .models import Necessidade

@receiver(post_save, sender=Necessidade)
def enviar_email_criacao_anuncio(sender, instance, created, **kwargs):
    """
    Sempre que um Necessidade é criado (created=True),
    enviamos um e-mail ao cliente.
    """
    if created:
        user = instance.cliente
        assunto = "Novo Anúncio Criado"
        corpo = (
            f"Olá, {user.first_name}!\n\n"
            "Seu novo anúncio foi criado com sucesso. "
            f"Título do anúncio: {instance.titulo}\n"
            "Muito obrigado por usar nossa plataforma.\n\n"
            "Atenciosamente,\nNecessito"
        )
        destinatario = [user.email]

        send_mail(
            subject=assunto,
            message=corpo,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=destinatario,
            fail_silently=False
        )
