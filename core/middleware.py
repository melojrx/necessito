"""
middleware.py - Core App
Middleware para sugestão de completar perfil após login (não obrigatório)
"""

from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages
import logging

logger = logging.getLogger(__name__)


class ProfileCompleteMiddleware:
    """
    Middleware que sugere ao usuário completar perfil após login.
    NÃO bloqueia o acesso - apenas redireciona uma vez e permite pular.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Processar request antes da view
        if self._should_suggest_profile_completion(request):
            # Debug info
            logger.info(f"Suggesting profile completion for user {request.user.id} from {request.path}")
            
            messages.info(
                request, 
                "Complete seu perfil para ter uma experiência completa na plataforma!"
            )
            
            # Marcar que já sugerimos o perfil para este usuário nesta sessão
            request.session['profile_completion_suggested'] = True
            
            return redirect('complete_profile')
        
        response = self.get_response(request)
        return response

    def _should_suggest_profile_completion(self, request):
        """
        Verifica se deve sugerir completar perfil
        Lógica suave: apenas uma vez por sessão, após login
        """
        # Debug info
        logger.debug(f"Checking suggestion for user: {request.user}, path: {request.path}")
        
        # Usuário deve estar logado
        if not request.user.is_authenticated:
            logger.debug("User not authenticated, skipping")
            return False
            
        # Verificar se o perfil já está completo
        if self._is_profile_complete(request.user):
            logger.debug(f"Profile complete for user {request.user.id}")
            return False
            
        # Verificar se já sugerimos ou usuário pulou nesta sessão
        if request.session.get('profile_completion_suggested', False):
            logger.debug("Profile completion already suggested in this session")
            return False
            
        if request.session.get('profile_completion_skipped', False):
            logger.debug("User skipped profile completion in this session")
            return False
            
        # Verificar se não está em URLs que devem ser permitidas
        if self._is_exempt_url(request.path):
            logger.debug(f"URL {request.path} is exempt")
            return False
            
        # Verificar se não é uma requisição AJAX
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            logger.debug("AJAX request, skipping")
            return False
            
        # Verificar se não é um POST para evitar interferir com forms
        if request.method == 'POST':
            logger.debug("POST request, skipping")
            return False
            
        # Verificar se o usuário acabou de fazer login
        # Apenas sugerir em páginas principais, não em todas
        if not self._is_main_page(request.path):
            logger.debug(f"Not a main page: {request.path}")
            return False
            
        logger.debug(f"Should suggest profile completion to user {request.user.id}")
        return True

    def _is_profile_complete(self, user):
        """
        Verifica se o perfil do usuário está completo.
        Critérios: deve ter is_client OU is_supplier = True
        """
        return user.is_client or user.is_supplier

    def _is_exempt_url(self, path):
        """
        URLs que nunca devem acionar o redirecionamento
        """
        exempt_patterns = [
            '/users/complete-profile/',  # Página de completar perfil
            '/complete-profile/',        
            '/users/logout/',
            '/logout/',
            '/static/',
            '/media/',
            '/admin/',
            '/api/',
            '/favicon.ico',
            '/accounts/',
            '/users/login/',
            '/users/register/',
            '/login/',
            '/register/',
            '/ajuda/',  # Central de ajuda
            '/help/',
        ]
        
        return any(path.startswith(pattern) for pattern in exempt_patterns)
    
    def _is_main_page(self, path):
        """
        Páginas principais onde é apropriado sugerir completar perfil
        """
        main_pages = [
            '/',          # Homepage
            '/home/',     # Dashboard
            '/dashboard/',
            '/anuncios/', # Páginas de anúncios
            '/buscar/',   # Busca
            '/search/',
        ]
        
        return any(path.startswith(page) for page in main_pages) or path == '/' 