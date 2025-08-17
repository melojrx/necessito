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
        Verifica se o usuário pode editar um anúncio usando o state machine.
        Regra: Deve ser o cliente que criou o anúncio e estado deve permitir edição.
        """
        if isinstance(user, AnonymousUser) or not user.is_authenticated:
            return False, "Você precisa estar logado."
        
        if user != ad.cliente:
            return False, "Você só pode editar seus próprios anúncios."
        
        # Use state machine logic
        if not ad.can_be_edited(user):
            return False, "Não é possível editar anúncios que possuem orçamentos ou já foram finalizados."
        
        return True, ""
    
    @staticmethod
    def can_edit_budget(user, budget):
        """
        Verifica se o usuário pode editar um orçamento usando o state machine.
        Regra: Deve ser o fornecedor que criou o orçamento e status deve permitir edição.
        """
        if isinstance(user, AnonymousUser) or not user.is_authenticated:
            return False, "Você precisa estar logado."
        
        if user != budget.fornecedor:
            return False, "Você só pode editar seus próprios orçamentos."
        
        # Use state machine logic
        if not budget.can_be_edited(user):
            return False, "Não é possível editar orçamentos já processados."
        
        return True, ""
    
    @staticmethod
    def can_accept_budget(user, budget):
        """
        Verifica se o usuário pode aceitar um orçamento usando o state machine.
        Regra: Deve ser o cliente dono do anúncio.
        """
        if isinstance(user, AnonymousUser) or not user.is_authenticated:
            return False, "Você precisa estar logado."
        
        if user != budget.anuncio.cliente:
            return False, "Apenas o cliente que criou o anúncio pode aceitar orçamentos."
        
        # Use state machine logic
        if not budget.can_be_accepted(user):
            return False, "Este orçamento não pode ser aceito no momento."
        
        return True, ""
    
    @staticmethod
    def can_reject_budget(user, budget):
        """
        Verifica se o usuário pode rejeitar um orçamento usando o state machine.
        Regra: Deve ser o cliente dono do anúncio.
        """
        if isinstance(user, AnonymousUser) or not user.is_authenticated:
            return False, "Você precisa estar logado."
        
        if user != budget.anuncio.cliente:
            return False, "Apenas o cliente que criou o anúncio pode rejeitar orçamentos."
        
        # Use state machine logic
        if not budget.can_be_rejected(user):
            return False, "Este orçamento não pode ser rejeitado no momento."
        
        return True, ""
    
    @staticmethod
    def can_finalize_ad(user, ad):
        """
        Verifica se o usuário pode finalizar um anúncio usando o state machine.
        Regra: Deve ser o cliente dono do anúncio e estar em estado apropriado.
        """
        if isinstance(user, AnonymousUser) or not user.is_authenticated:
            return False, "Você precisa estar logado."
        
        if user != ad.cliente:
            return False, "Apenas o cliente que criou o anúncio pode finalizá-lo."
        
        # Use state machine logic
        if not ad.can_be_finalized(user):
            return False, "O anúncio não pode ser finalizado no momento."
        
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
    
    # ==================== STATE MACHINE PERMISSIONS ====================
    
    @staticmethod
    def can_confirm_budget(user, budget):
        """
        Verifica se o usuário pode confirmar um orçamento.
        Regra: Deve ser o fornecedor e orçamento deve estar aceito pelo cliente.
        """
        if isinstance(user, AnonymousUser) or not user.is_authenticated:
            return False, "Você precisa estar logado."
        
        if user != budget.fornecedor:
            return False, "Apenas o fornecedor pode confirmar o orçamento."
        
        # Use state machine logic
        if not budget.can_be_confirmed(user):
            return False, "Este orçamento não pode ser confirmado no momento."
        
        return True, ""
    
    @staticmethod
    def can_refuse_budget(user, budget):
        """
        Verifica se o usuário pode recusar um orçamento.
        Regra: Deve ser o fornecedor e orçamento deve estar aceito pelo cliente.
        """
        if isinstance(user, AnonymousUser) or not user.is_authenticated:
            return False, "Você precisa estar logado."
        
        if user != budget.fornecedor:
            return False, "Apenas o fornecedor pode recusar o orçamento."
        
        # Use state machine logic
        if not budget.can_be_refused(user):
            return False, "Este orçamento não pode ser recusado no momento."
        
        return True, ""
    
    @staticmethod
    def can_cancel_ad(user, ad):
        """
        Verifica se o usuário pode cancelar um anúncio.
        Regra: Deve ser o cliente dono do anúncio.
        """
        if isinstance(user, AnonymousUser) or not user.is_authenticated:
            return False, "Você precisa estar logado."
        
        if user != ad.cliente:
            return False, "Apenas o cliente que criou o anúncio pode cancelá-lo."
        
        # Use state machine logic
        if not ad.can_be_cancelled(user):
            return False, "Este anúncio não pode ser cancelado no momento."
        
        return True, ""
    
    @staticmethod
    def can_transition_necessidade(user, necessidade, new_status):
        """
        Verifica se o usuário pode fazer uma transição específica na necessidade.
        """
        if isinstance(user, AnonymousUser) or not user.is_authenticated:
            return False, "Você precisa estar logado."
        
        # Check if transition is valid using state machine
        can_transition, message = necessidade.can_transition_to(new_status, user=user)
        return can_transition, message
    
    @staticmethod
    def can_transition_orcamento(user, orcamento, new_status):
        """
        Verifica se o usuário pode fazer uma transição específica no orçamento.
        """
        if isinstance(user, AnonymousUser) or not user.is_authenticated:
            return False, "Você precisa estar logado."
        
        # Check if transition is valid using state machine
        can_transition, message = orcamento.can_transition_to(new_status, user=user)
        return can_transition, message

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