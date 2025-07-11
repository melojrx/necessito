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


def validate_password_strength(password: str) -> str:
    """
    Valida a força de uma senha baseada em critérios de segurança.
    
    Critérios:
    - Mínimo 8 caracteres
    - Pelo menos 1 letra maiúscula
    - Pelo menos 1 letra minúscula
    - Pelo menos 1 dígito
    - Pelo menos 1 caractere especial
    - Não pode ser uma senha comum
    
    Args:
        password (str): A senha a ser validada
        
    Returns:
        str: A senha validada
        
    Raises:
        ValidationError: Se a senha não atender aos critérios
    """
    
    # Lista de senhas comuns que devem ser rejeitadas
    COMMON_PASSWORDS = [
        '123456', 'password', '123456789', '12345678', '12345', '1234567',
        'qwerty', 'abc123', 'password123', '123123', 'admin', 'letmein',
        'welcome', 'monkey', '1234567890', 'dragon', 'master', 'hello',
        'freedom', 'whatever', 'qazwsx', 'trustno1', 'batman', 'zaq1zaq1'
    ]
    
    errors = []
    
    # Verificar comprimento mínimo
    if len(password) < 8:
        errors.append("A senha deve ter pelo menos 8 caracteres.")
    
    # Verificar se tem pelo menos uma letra maiúscula
    if not re.search(r'[A-Z]', password):
        errors.append("A senha deve conter pelo menos uma letra maiúscula.")
    
    # Verificar se tem pelo menos uma letra minúscula
    if not re.search(r'[a-z]', password):
        errors.append("A senha deve conter pelo menos uma letra minúscula.")
    
    # Verificar se tem pelo menos um dígito
    if not re.search(r'\d', password):
        errors.append("A senha deve conter pelo menos um número.")
    
    # Verificar se tem pelo menos um caractere especial
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        errors.append("A senha deve conter pelo menos um caractere especial (!@#$%^&*(),.?\":{}|<>).")
    
    # Verificar se não é uma senha comum
    if password.lower() in [p.lower() for p in COMMON_PASSWORDS]:
        errors.append("Esta senha é muito comum. Escolha uma senha mais segura.")
    
    # Verificar se não é uma sequência simples
    if re.search(r'(012|123|234|345|456|567|678|789|890|abc|bcd|cde|def)', password.lower()):
        errors.append("A senha não pode conter sequências simples (123, abc, etc.).")
    
    # Verificar se não tem muitos caracteres repetidos
    if re.search(r'(.)\1{2,}', password):
        errors.append("A senha não pode ter mais de 2 caracteres iguais consecutivos.")
    
    # Se houver erros, lançar ValidationError
    if errors:
        raise ValidationError(errors)
    
    return password


def get_password_strength_score(password: str) -> dict:
    """
    Calcula a pontuação de força da senha de 0 a 100.
    
    Args:
        password (str): A senha a ser avaliada
        
    Returns:
        dict: Dicionário com score, nível e sugestões
    """
    
    score = 0
    suggestions = []
    
    # Comprimento (0-25 pontos)
    if len(password) >= 8:
        score += 10
    if len(password) >= 12:
        score += 10
    if len(password) >= 16:
        score += 5
    else:
        suggestions.append("Use pelo menos 12 caracteres para maior segurança.")
    
    # Variedade de caracteres (0-40 pontos)
    if re.search(r'[a-z]', password):
        score += 10
    else:
        suggestions.append("Adicione letras minúsculas.")
        
    if re.search(r'[A-Z]', password):
        score += 10
    else:
        suggestions.append("Adicione letras maiúsculas.")
        
    if re.search(r'\d', password):
        score += 10
    else:
        suggestions.append("Adicione números.")
        
    if re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        score += 10
    else:
        suggestions.append("Adicione caracteres especiais.")
    
    # Complexidade (0-35 pontos)
    if not re.search(r'(.)\1{2,}', password):
        score += 10  # Sem repetições excessivas
    
    if not re.search(r'(012|123|234|345|456|567|678|789|890|abc|bcd|cde|def)', password.lower()):
        score += 10  # Sem sequências simples
    
    # Mistura de tipos de caracteres
    char_types = sum([
        bool(re.search(r'[a-z]', password)),
        bool(re.search(r'[A-Z]', password)),
        bool(re.search(r'\d', password)),
        bool(re.search(r'[!@#$%^&*(),.?":{}|<>]', password))
    ])
    
    if char_types >= 3:
        score += 10
    if char_types == 4:
        score += 5
    
    # Determinar nível
    if score >= 80:
        level = "Muito Forte"
        color = "success"
    elif score >= 60:
        level = "Forte"
        color = "info"
    elif score >= 40:
        level = "Média"
        color = "warning"
    else:
        level = "Fraca"
        color = "danger"
    
    return {
        'score': score,
        'level': level,
        'color': color,
        'suggestions': suggestions
    }


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