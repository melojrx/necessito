# chat/auth.py

import logging
from django.contrib.auth import get_user_model
from django.contrib.sessions.models import Session
from django.utils import timezone
from urllib.parse import parse_qs

User = get_user_model()
logger = logging.getLogger(__name__)

def get_user_from_socket_session(environ):
    """
    Extrai o usuário autenticado da sessão do Socket.IO
    """
    try:
        # Extrair parâmetros da query string
        query_string = environ.get('QUERY_STRING', '')
        params = parse_qs(query_string)
        
        # Método 1: Via session_key na query string
        session_key = params.get('session_key', [None])[0]
        if session_key:
            try:
                session = Session.objects.get(
                    session_key=session_key,
                    expire_date__gt=timezone.now()
                )
                user_id = session.get_decoded().get('_auth_user_id')
                if user_id:
                    user = User.objects.get(id=user_id)
                    return user
            except (Session.DoesNotExist, User.DoesNotExist):
                pass
        
        # Método 2: Via token de autenticação (implementar se necessário)
        auth_token = params.get('token', [None])[0]
        if auth_token:
            # Implementar validação de token JWT/personalizado
            # user = validate_auth_token(auth_token)
            # return user
            pass
        
        # Método 3: Via cabeçalhos HTTP (cookies)
        headers = environ.get('HTTP_COOKIE', '')
        if 'sessionid=' in headers:
            # Extrair sessionid do cookie
            import re
            match = re.search(r'sessionid=([^;]+)', headers)
            if match:
                session_id = match.group(1)
                try:
                    session = Session.objects.get(
                        session_key=session_id,
                        expire_date__gt=timezone.now()
                    )
                    user_id = session.get_decoded().get('_auth_user_id')
                    if user_id:
                        user = User.objects.get(id=user_id)
                        return user
                except (Session.DoesNotExist, User.DoesNotExist):
                    pass
        
        return None
        
    except Exception as e:
        logger.error(f"Erro ao extrair usuário da sessão: {e}")
        return None

def validate_auth_token(token):
    """
    Valida token de autenticação personalizado
    Implementar conforme necessário
    """
    try:
        # Exemplo de implementação com JWT
        # import jwt
        # payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        # user_id = payload.get('user_id')
        # user = User.objects.get(id=user_id)
        # return user
        pass
    except Exception as e:
        logger.error(f"Erro ao validar token: {e}")
        return None

def create_auth_token(user):
    """
    Cria token de autenticação para WebSocket
    """
    try:
        # Exemplo com JWT
        # import jwt
        # from django.conf import settings
        # payload = {
        #     'user_id': user.id,
        #     'exp': timezone.now() + timedelta(hours=24)
        # }
        # token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
        # return token
        pass
    except Exception as e:
        logger.error(f"Erro ao criar token: {e}")
        return None 