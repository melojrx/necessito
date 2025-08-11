# core/mixins.py
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse_lazy
from django.core.exceptions import PermissionDenied

class ClientRequiredMixin(LoginRequiredMixin):
    """
    Mixin que requer que o usuário seja um cliente.
    """
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        
        if not request.user.is_client:
            messages.warning(
                request, 
                "Para acessar esta funcionalidade, você precisa completar seu perfil como cliente."
            )
            return redirect('users:complete_profile')
        
        return super().dispatch(request, *args, **kwargs)

class SupplierRequiredMixin(LoginRequiredMixin):
    """
    Mixin que requer que o usuário seja um fornecedor.
    """
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        
        if not request.user.is_supplier:
            messages.warning(
                request, 
                "Para acessar esta funcionalidade, você precisa completar seu perfil como fornecedor."
            )
            return redirect('users:complete_profile')
        
        return super().dispatch(request, *args, **kwargs)

class ProfileCompleteRequiredMixin(LoginRequiredMixin):
    """
    Mixin que requer que o usuário tenha perfil completo (cliente ou fornecedor).
    """
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        
        if not (request.user.is_client or request.user.is_supplier):
            messages.info(
                request, 
                "Complete seu perfil para acessar esta funcionalidade."
            )
            return redirect('users:complete_profile')
        
        return super().dispatch(request, *args, **kwargs)

class EmailVerifiedRequiredMixin(LoginRequiredMixin):
    """
    Mixin que requer que o usuário tenha e-mail verificado.
    """
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        
        if not request.user.email_verified:
            messages.warning(
                request, 
                "Você precisa verificar seu e-mail para acessar esta funcionalidade."
            )
            return redirect('email_verification_notice')
        
        return super().dispatch(request, *args, **kwargs)

class AdminRequiredMixin(LoginRequiredMixin):
    """
    Mixin que requer que o usuário seja administrador.
    """
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        
        if not request.user.is_staff:
            raise PermissionDenied("Você não tem permissão para acessar esta página.")
        
        return super().dispatch(request, *args, **kwargs)

class OwnerRequiredMixin(LoginRequiredMixin):
    """
    Mixin que requer que o usuário seja o proprietário do objeto.
    Define owner_field para especificar o campo que representa o proprietário.
    """
    owner_field = 'cliente'  # Campo padrão
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        
        obj = self.get_object()
        owner = getattr(obj, self.owner_field, None)
        
        if owner != request.user:
            raise PermissionDenied("Você não tem permissão para acessar este recurso.")
        
        return super().dispatch(request, *args, **kwargs)

class ClientOrSupplierRequiredMixin(LoginRequiredMixin):
    """
    Mixin que permite acesso tanto para clientes quanto para fornecedores.
    Útil para funcionalidades que ambos os tipos de usuário podem usar.
    """
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        
        if not (request.user.is_client or request.user.is_supplier):
            messages.info(
                request, 
                "Complete seu perfil para acessar esta funcionalidade."
            )
            return redirect('users:complete_profile')
        
        return super().dispatch(request, *args, **kwargs)

class BudgetOwnerMixin(LoginRequiredMixin):
    """
    Mixin específico para orçamentos - permite acesso ao fornecedor que criou
    o orçamento ou ao cliente dono do anúncio.
    """
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        
        obj = self.get_object()
        
        # Verificar se é o fornecedor do orçamento ou o cliente do anúncio
        if (request.user != obj.fornecedor and 
            request.user != obj.anuncio.cliente):
            raise PermissionDenied("Você não tem permissão para acessar este orçamento.")
        
        return super().dispatch(request, *args, **kwargs)