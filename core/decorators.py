# core/decorators.py (crie este arquivo se não existir)
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect, render
from django.contrib import messages

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