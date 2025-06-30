import re
from django.core.exceptions import ValidationError

def validate_cpf(cpf: str) -> str:
    """
    Valida um CPF e devolve somente os 11 dígitos se for válido.
    Lança ValidationError em caso de erro.
    """

    # Mantém só os dígitos
    cpf_num = re.sub(r'\D', '', cpf)

    if len(cpf_num) != 11:
        raise ValidationError("CPF deve ter 11 dígitos.")

    # Rejeita sequências repetidas (000… / 111… etc.)
    if cpf_num == cpf_num[0] * 11:
        raise ValidationError("CPF inválido (sequência repetida).")

    digitos = list(map(int, cpf_num))

    # ---------- primeiro dígito verificador ----------
    soma_1 = sum(d * p for d, p in zip(digitos[:9], range(10, 1, -1)))   # pesos 10..2
    resto_1 = (soma_1 * 10) % 11
    dv1 = 0 if resto_1 == 10 else resto_1
    if dv1 != digitos[9]:
        raise ValidationError("CPF inválido (1º dígito verificador).")

    # ---------- segundo dígito verificador ----------
    soma_2 = sum(d * p for d, p in zip(digitos[:10], range(11, 1, -1)))  # pesos 11..2
    resto_2 = (soma_2 * 10) % 11
    dv2 = 0 if resto_2 == 10 else resto_2
    if dv2 != digitos[10]:
        raise ValidationError("CPF inválido (2º dígito verificador).")

    # Se chegou aqui, CPF é válido
    return cpf_num


def send_email_verification(user, request):
    """
    Envia e-mail de verificação para o usuário.
    
    Args:
        user: Instância do modelo User
        request: Request HTTP para obter domínio atual
        
    Returns:
        bool: True se o e-mail foi enviado com sucesso
    """
    from django.core.mail import send_mail
    from django.template.loader import render_to_string
    from django.contrib.sites.shortcuts import get_current_site
    from django.conf import settings
    from django.urls import reverse
    
    try:
        # Gera token de verificação
        token = user.generate_email_verification_token()
        
        # Obtém o site atual
        current_site = get_current_site(request)
        
        # Monta URL de verificação
        verification_url = request.build_absolute_uri(
            reverse('verify_email', kwargs={'token': token})
        )
        
        # Contexto para o template
        context = {
            'user': user,
            'domain': current_site.domain,
            'site_name': current_site.name,
            'verification_url': verification_url,
            'token': token,
        }
        
        # Renderiza o template do e-mail
        subject = f'[{current_site.name}] Confirme seu e-mail'
        html_message = render_to_string('users/email/verification_email.html', context)
        plain_message = render_to_string('users/email/verification_email.txt', context)
        
        # Envia o e-mail
        success = send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False
        )
        
        return success == 1
        
    except Exception as e:
        # Log do erro (em produção, usar logging apropriado)
        print(f"Erro ao enviar e-mail de verificação: {e}")
        return False


def resend_email_verification(user, request):
    """
    Reenvia e-mail de verificação se o anterior expirou ou o usuário solicitou.
    
    Args:
        user: Instância do modelo User
        request: Request HTTP
        
    Returns:
        tuple: (success: bool, message: str)
    """
    from django.utils import timezone
    from datetime import timedelta
    
    # Verifica se já está verificado
    if user.email_verified:
        return False, "Seu e-mail já está verificado."
    
    # Verifica se pode reenviar (limite de 1 e-mail a cada 5 minutos)
    if user.email_verification_sent_at:
        time_since_last = timezone.now() - user.email_verification_sent_at
        if time_since_last < timedelta(minutes=5):
            minutes_left = 5 - int(time_since_last.total_seconds() / 60)
            return False, f"Aguarde {minutes_left} minuto(s) para reenviar."
    
    # Envia novo e-mail
    success = send_email_verification(user, request)
    
    if success:
        return True, "E-mail de verificação reenviado com sucesso!"
    else:
        return False, "Erro ao enviar e-mail. Tente novamente em instantes."