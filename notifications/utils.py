from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib.sites.models import Site


def send_notification_email(template_name, subject, recipient_email, context=None):
    """
    Envia e-mail de notificação usando templates HTML e texto.
    
    Args:
        template_name: Nome do template (sem extensão)
        subject: Assunto do e-mail
        recipient_email: E-mail do destinatário
        context: Dicionário com contexto para o template
    """
    if context is None:
        context = {}
    
    # Adiciona domínio ao contexto
    current_site = Site.objects.get_current()
    context['domain'] = current_site.domain
    
    # Renderiza templates HTML e texto
    html_template = f'notifications/email/{template_name}.html'
    text_template = f'notifications/email/{template_name}.txt'
    
    html_content = render_to_string(html_template, context)
    text_content = render_to_string(text_template, context)
    
    # Cria e envia e-mail
    msg = EmailMultiAlternatives(
        subject=subject,
        body=text_content,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[recipient_email]
    )
    msg.attach_alternative(html_content, "text/html")
    
    try:
        msg.send()
        return True
    except Exception as e:
        print(f"Erro ao enviar e-mail: {e}")
        return False


def get_anuncio_url(anuncio):
    """
    Gera URL completa para um anúncio.
    """
    current_site = Site.objects.get_current()
    return f"http://{current_site.domain}/anuncio/{anuncio.id}/"


def get_perfil_url(user):
    """
    Gera URL completa para o perfil de um usuário.
    """
    current_site = Site.objects.get_current()
    return f"http://{current_site.domain}/users/perfil/{user.id}/"


def get_avaliacao_url(anuncio):
    """
    Gera URL para página de avaliação.
    """
    current_site = Site.objects.get_current()
    return f"http://{current_site.domain}/avaliar/{anuncio.id}/" 