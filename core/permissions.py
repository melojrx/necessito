# core/permissions.py
"""
Sistema centralizado de permissões para o Indicai.
Contém funções utilitárias para verificação de permissões específicas.
"""

from django.core.exceptions import PermissionDenied
from django.contrib.auth.models import AnonymousUser

class PermissionValidator:
    """
    Classe utilitária para validações de permissões.
    """
    
    @staticmethod
    def can_create_ad(user):
        """
        Verifica se o usuário pode criar anúncios.
        Regra: Deve ser cliente e ter e-mail verificado.
        """
        if isinstance(user, AnonymousUser) or not user.is_authenticated:
            return False, "Você precisa estar logado para criar anúncios."
        
        if not user.email_verified:
            return False, "Você precisa verificar seu e-mail para criar anúncios."
        
        if not user.is_client:
            return False, "Você precisa completar seu perfil como cliente para criar anúncios."
        
        return True, ""
    
    @staticmethod
    def can_create_budget(user):
        """
        Verifica se o usuário pode criar orçamentos.
        Regra: Deve ser fornecedor e ter e-mail verificado.
        """
        if isinstance(user, AnonymousUser) or not user.is_authenticated:
            return False, "Você precisa estar logado para criar orçamentos."
        
        if not user.email_verified:
            return False, "Você precisa verificar seu e-mail para criar orçamentos."
        
        if not user.is_supplier:
            return False, "Você precisa completar seu perfil como fornecedor para criar orçamentos."
        
        return True, ""
    
    @staticmethod
    def can_edit_ad(user, ad):
        """
        Verifica se o usuário pode editar um anúncio.
        Regra: Deve ser o cliente que criou o anúncio.
        """
        if isinstance(user, AnonymousUser) or not user.is_authenticated:
            return False, "Você precisa estar logado."
        
        if user != ad.cliente:
            return False, "Você só pode editar seus próprios anúncios."
        
        if ad.status in ['analisando_orcamentos', 'aguardando_confirmacao', 'em_atendimento', 'finalizado', 'cancelado']:
            return False, "Não é possível editar anúncios que possuem orçamentos ou já foram finalizados."
        
        return True, ""
    
    @staticmethod
    def can_edit_budget(user, budget):
        """
        Verifica se o usuário pode editar um orçamento.
        Regra: Deve ser o fornecedor que criou o orçamento e status deve permitir edição.
        """
        if isinstance(user, AnonymousUser) or not user.is_authenticated:
            return False, "Você precisa estar logado."
        
        if user != budget.fornecedor:
            return False, "Você só pode editar seus próprios orçamentos."
        
        if budget.status in ['aceito_pelo_cliente', 'confirmado', 'rejeitado']:
            return False, "Não é possível editar orçamentos já processados."
        
        return True, ""
    
    @staticmethod
    def can_accept_budget(user, budget):
        """
        Verifica se o usuário pode aceitar um orçamento.
        Regra: Deve ser o cliente dono do anúncio.
        """
        if isinstance(user, AnonymousUser) or not user.is_authenticated:
            return False, "Você precisa estar logado."
        
        if user != budget.anuncio.cliente:
            return False, "Apenas o cliente que criou o anúncio pode aceitar orçamentos."
        
        if budget.status != 'pendente':
            return False, "Este orçamento já foi processado."
        
        return True, ""
    
    @staticmethod
    def can_reject_budget(user, budget):
        """
        Verifica se o usuário pode rejeitar um orçamento.
        Regra: Deve ser o cliente dono do anúncio.
        """
        if isinstance(user, AnonymousUser) or not user.is_authenticated:
            return False, "Você precisa estar logado."
        
        if user != budget.anuncio.cliente:
            return False, "Apenas o cliente que criou o anúncio pode rejeitar orçamentos."
        
        if budget.status != 'pendente':
            return False, "Este orçamento já foi processado."
        
        return True, ""
    
    @staticmethod
    def can_finalize_ad(user, ad):
        """
        Verifica se o usuário pode finalizar um anúncio.
        Regra: Deve ser o cliente dono do anúncio e ter orçamento aceito.
        """
        if isinstance(user, AnonymousUser) or not user.is_authenticated:
            return False, "Você precisa estar logado."
        
        if user != ad.cliente:
            return False, "Apenas o cliente que criou o anúncio pode finalizá-lo."
        
        if ad.status != 'em_atendimento':
            return False, "O anúncio deve estar em atendimento para ser finalizado."
        
        # Verificar se há orçamento aceito
        has_accepted_budget = ad.orcamentos.filter(status='confirmado').exists()
        if not has_accepted_budget:
            return False, "Não há orçamentos aceitos para este anúncio."
        
        return True, ""
    
    @staticmethod
    def can_evaluate(user, ad):
        """
        Verifica se o usuário pode avaliar em um anúncio.
        Regra: Deve ser o cliente ou o fornecedor do orçamento aceito.
        """
        if isinstance(user, AnonymousUser) or not user.is_authenticated:
            return False, "Você precisa estar logado."
        
        if ad.status != 'finalizado':
            return False, "Avaliações só podem ser feitas após a finalização do anúncio."
        
        # Verificar se é o cliente
        if user == ad.cliente:
            return True, ""
        
        # Verificar se é o fornecedor de algum orçamento aceito
        accepted_budget = ad.orcamentos.filter(status='confirmado').first()
        if accepted_budget and user == accepted_budget.fornecedor:
            return True, ""
        
        return False, "Você não tem permissão para avaliar este anúncio."
    
    @staticmethod
    def can_view_budget_details(user, budget):
        """
        Verifica se o usuário pode ver os detalhes de um orçamento.
        Regra: Deve ser o fornecedor que criou ou o cliente dono do anúncio.
        """
        if isinstance(user, AnonymousUser) or not user.is_authenticated:
            return False, "Você precisa estar logado."
        
        if user == budget.fornecedor or user == budget.anuncio.cliente:
            return True, ""
        
        return False, "Você não tem permissão para ver este orçamento."
    
    @staticmethod
    def can_access_dashboard(user):
        """
        Verifica se o usuário pode acessar o dashboard.
        Regra: Deve ser administrador.
        """
        if isinstance(user, AnonymousUser) or not user.is_authenticated:
            return False, "Você precisa estar logado."
        
        if not user.is_staff:
            return False, "Apenas administradores podem acessar o dashboard."
        
        return True, ""

def require_permission(permission_func, *args, **kwargs):
    """
    Decorator helper para aplicar verificações de permissão.
    """
    def decorator(view_func):
        def wrapper(request, *view_args, **view_kwargs):
            can_access, message = permission_func(request.user, *args, **kwargs)
            if not can_access:
                raise PermissionDenied(message)
            return view_func(request, *view_args, **view_kwargs)
        return wrapper
    return decorator