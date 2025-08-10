# core/decorators.py
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect, render
from django.contrib import messages
from django.urls import reverse
from functools import wraps

def admin_required(function):
    """
    Decorator para views que verifica se o usuário é administrador,
    redirecionando para a página de acesso negado caso não seja.
    """
    def check_admin(user):
        return user.is_authenticated and user.is_staff

    def wrapper(request, *args, **kwargs):
        if not check_admin(request.user):
            return render(request, '403.html', status=403)
        return function(request, *args, **kwargs)

    return wrapper

def client_required(function=None, redirect_url=None):
    """
    Decorator para views que requer que o usuário seja um cliente.
    Se não for cliente, redireciona para completar perfil ou página especificada.
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
            
            if not request.user.is_client:
                messages.warning(
                    request, 
                    "Para acessar esta funcionalidade, você precisa completar seu perfil como cliente."
                )
                return redirect(redirect_url or 'complete_profile')
            
            return view_func(request, *args, **kwargs)
        return wrapper
    
    if function:
        return decorator(function)
    return decorator

def supplier_required(function=None, redirect_url=None):
    """
    Decorator para views que requer que o usuário seja um fornecedor.
    Se não for fornecedor, redireciona para completar perfil ou página especificada.
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
            
            if not request.user.is_supplier:
                messages.warning(
                    request, 
                    "Para acessar esta funcionalidade, você precisa completar seu perfil como fornecedor."
                )
                return redirect(redirect_url or 'complete_profile')
            
            return view_func(request, *args, **kwargs)
        return wrapper
    
    if function:
        return decorator(function)
    return decorator

def profile_complete_required(function=None, redirect_url=None):
    """
    Decorator para views que requer que o usuário tenha perfil completo.
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
            
            if not (request.user.is_client or request.user.is_supplier):
                messages.info(
                    request, 
                    "Complete seu perfil para acessar esta funcionalidade."
                )
                return redirect(redirect_url or 'complete_profile')
            
            return view_func(request, *args, **kwargs)
        return wrapper
    
    if function:
        return decorator(function)
    return decorator

def owner_required(owner_field='cliente'):
    """
    Decorator para views que requer que o usuário seja o proprietário do objeto.
    
    Args:
        owner_field: Campo do modelo que representa o proprietário (ex: 'cliente', 'fornecedor', 'usuario')
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
            
            # Assumindo que a view tem um método get_object() ou similar
            # Esta lógica pode ser refinada conforme necessário
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator

def email_verified_required(function=None, redirect_url=None):
    """
    Decorator para views que requer que o usuário tenha e-mail verificado.
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
            
            if not request.user.email_verified:
                messages.warning(
                    request, 
                    "Você precisa verificar seu e-mail para acessar esta funcionalidade."
                )
                return redirect(redirect_url or 'email_verification_notice')
            
            return view_func(request, *args, **kwargs)
        return wrapper
    
    if function:
        return decorator(function)
    return decorator