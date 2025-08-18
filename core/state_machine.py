"""
State Machine implementation for Necessidade and Orçamento models.
Provides robust state management with business rule compliance and automatic transitions.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Callable, Any
from django.db import transaction
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

logger = logging.getLogger(__name__)

User = get_user_model()


class StateTransitionError(Exception):
    """Raised when an invalid state transition is attempted."""
    pass


class StateMachineBase:
    """
    Base class for state machines with transaction safety and audit trail.
    """
    
    def __init__(self, instance):
        self.instance = instance
        self.transitions = {}
        self.side_effects = {}
        self.conditions = {}
        self._setup_transitions()
        self._setup_conditions()
        self._setup_side_effects()
    
    def _setup_transitions(self):
        """Override in subclasses to define valid transitions."""
        raise NotImplementedError("Subclasses must implement _setup_transitions")
    
    def _setup_conditions(self):
        """Override in subclasses to define transition conditions."""
        pass
    
    def _setup_side_effects(self):
        """Override in subclasses to define transition side effects."""
        pass
    
    def add_transition(self, from_state: str, to_state: str, condition: Optional[Callable] = None):
        """Add a valid transition between states."""
        if from_state not in self.transitions:
            self.transitions[from_state] = []
        self.transitions[from_state].append(to_state)
        
        if condition:
            self.conditions[(from_state, to_state)] = condition
    
    def add_side_effect(self, transition: Tuple[str, str], effect: Callable):
        """Add a side effect to be executed after a transition."""
        self.side_effects[transition] = effect
    
    def can_transition(self, to_state: str, user: Optional[User] = None, **kwargs) -> Tuple[bool, str]:
        """
        Check if transition to the given state is valid.
        Returns (is_valid, error_message).
        """
        current_state = self.get_current_state()
        
        # Check if transition exists
        if current_state not in self.transitions:
            return False, f"No transitions defined from state '{current_state}'"
        
        if to_state not in self.transitions[current_state]:
            return False, f"Invalid transition from '{current_state}' to '{to_state}'"
        
        # Check conditions
        condition_key = (current_state, to_state)
        if condition_key in self.conditions:
            condition_result = self.conditions[condition_key](user=user, **kwargs)
            if isinstance(condition_result, tuple):
                is_valid, message = condition_result
                if not is_valid:
                    return False, message
            elif not condition_result:
                return False, f"Condition not met for transition from '{current_state}' to '{to_state}'"
        
        return True, ""
    
    def transition_to(self, to_state: str, user: Optional[User] = None, **kwargs) -> bool:
        """
        Execute a state transition with transaction safety.
        Returns True if successful, raises StateTransitionError if invalid.
        """
        current_state = self.get_current_state()
        
        # Validate transition
        can_transition, error_message = self.can_transition(to_state, user, **kwargs)
        if not can_transition:
            logger.warning(f"Invalid transition attempt: {error_message}")
            raise StateTransitionError(error_message)
        
        try:
            with transaction.atomic():
                # Update state
                old_state = current_state
                self.set_state(to_state)
                
                # Update timestamps
                self._update_timestamps(old_state, to_state)
                
                # Execute side effects
                transition_key = (old_state, to_state)
                if transition_key in self.side_effects:
                    self.side_effects[transition_key](user=user, **kwargs)
                
                # Save instance (skip validation for automatic state transitions)
                self.instance.save(skip_validation=True)
                
                logger.info(f"State transition successful: {old_state} -> {to_state} for {self.instance}")
                return True
                
        except Exception as e:
            logger.error(f"State transition failed: {old_state} -> {to_state} for {self.instance}. Error: {str(e)}")
            raise StateTransitionError(f"Transition failed: {str(e)}")
    
    def get_current_state(self) -> str:
        """Get the current state of the instance."""
        return self.instance.status
    
    def set_state(self, new_state: str):
        """Set the state of the instance."""
        self.instance.status = new_state
    
    def _update_timestamps(self, old_state: str, new_state: str):
        """Update relevant timestamp fields based on state transition."""
        now = timezone.now()
        self.instance.modificado_em = now
    
    def get_valid_transitions(self) -> List[str]:
        """Get list of valid transitions from current state."""
        current_state = self.get_current_state()
        return self.transitions.get(current_state, [])
    
    def get_transition_history(self) -> List[Dict]:
        """Get the history of state transitions (if audit model exists)."""
        # This would be implemented if we had a StateTransitionLog model
        return []


class NecessidadeStateMachine(StateMachineBase):
    """
    State machine for Necessidade model with comprehensive business rules.
    """
    
    # Timeout configuration (in hours)
    CONFIRMATION_TIMEOUT = 48
    
    def _setup_transitions(self):
        """Define valid state transitions for Necessidade."""
        # From ativo
        self.add_transition('ativo', 'analisando_orcamentos')
        self.add_transition('ativo', 'cancelado')
        self.add_transition('ativo', 'expirado')
        
        # From analisando_orcamentos
        self.add_transition('analisando_orcamentos', 'aguardando_confirmacao')
        self.add_transition('analisando_orcamentos', 'cancelado')
        self.add_transition('analisando_orcamentos', 'expirado')
        
        # From aguardando_confirmacao
        self.add_transition('aguardando_confirmacao', 'em_atendimento')
        self.add_transition('aguardando_confirmacao', 'analisando_orcamentos')
        self.add_transition('aguardando_confirmacao', 'cancelado')
        self.add_transition('aguardando_confirmacao', 'expirado')
        
        # From em_atendimento
        self.add_transition('em_atendimento', 'finalizado')
        self.add_transition('em_atendimento', 'cancelado')
        self.add_transition('em_atendimento', 'em_disputa')
        
        
        # From em_disputa
        self.add_transition('em_disputa', 'em_atendimento')
        self.add_transition('em_disputa', 'finalizado')
        self.add_transition('em_disputa', 'cancelado')
        
        # From expirado (terminal state - can only be cancelled)
        self.add_transition('expirado', 'cancelado')
    
    def _setup_conditions(self):
        """Define transition conditions."""
        self.conditions[('ativo', 'analisando_orcamentos')] = self._condition_first_budget_received
        self.conditions[('analisando_orcamentos', 'aguardando_confirmacao')] = self._condition_budget_accepted_by_client
        self.conditions[('aguardando_confirmacao', 'em_atendimento')] = self._condition_budget_confirmed_by_supplier
        self.conditions[('aguardando_confirmacao', 'analisando_orcamentos')] = self._condition_budget_refused_by_supplier
        self.conditions[('em_atendimento', 'finalizado')] = self._condition_service_completed
        self.conditions[('em_atendimento', 'em_disputa')] = self._condition_can_open_dispute
        self.conditions[('em_disputa', 'em_atendimento')] = self._condition_dispute_resolved_continue
        self.conditions[('em_disputa', 'finalizado')] = self._condition_dispute_resolved_complete
        self.conditions[('em_disputa', 'cancelado')] = self._condition_dispute_resolved_cancel
    
    def _setup_side_effects(self):
        """Define side effects for transitions."""
        self.side_effects[('ativo', 'analisando_orcamentos')] = self._effect_first_budget_received
        self.side_effects[('analisando_orcamentos', 'aguardando_confirmacao')] = self._effect_budget_accepted
        self.side_effects[('aguardando_confirmacao', 'em_atendimento')] = self._effect_service_started
        self.side_effects[('aguardando_confirmacao', 'analisando_orcamentos')] = self._effect_budget_refused
        self.side_effects[('em_atendimento', 'finalizado')] = self._effect_service_completed
        self.side_effects[('ativo', 'cancelado')] = self._effect_cancelled
        self.side_effects[('analisando_orcamentos', 'cancelado')] = self._effect_cancelled
        self.side_effects[('aguardando_confirmacao', 'cancelado')] = self._effect_cancelled
        self.side_effects[('em_atendimento', 'cancelado')] = self._effect_cancelled
        self.side_effects[('em_atendimento', 'em_disputa')] = self._effect_dispute_opened
        self.side_effects[('em_disputa', 'em_atendimento')] = self._effect_dispute_resolved_continue
        self.side_effects[('em_disputa', 'finalizado')] = self._effect_dispute_resolved_complete
        self.side_effects[('em_disputa', 'cancelado')] = self._effect_dispute_resolved_cancel
    
    # Conditions
    def _condition_first_budget_received(self, **kwargs) -> Tuple[bool, str]:
        """Check if first budget has been received."""
        has_budgets = self.instance.orcamentos.filter(status='enviado').exists()
        if not has_budgets:
            return False, "Necessidade deve ter pelo menos um orçamento para mudar para 'analisando_orcamentos'"
        return True, ""
    
    def _condition_budget_accepted_by_client(self, user=None, budget=None, **kwargs) -> Tuple[bool, str]:
        """Check if client is accepting a budget."""
        if not user or not budget:
            return False, "Usuário e orçamento são obrigatórios"
        
        if user != self.instance.cliente:
            return False, "Apenas o cliente pode aceitar orçamentos"
        
        if budget.status != 'enviado':
            return False, "Apenas orçamentos 'enviado' podem ser aceitos"
        
        return True, ""
    
    def _condition_budget_confirmed_by_supplier(self, user=None, budget=None, **kwargs) -> Tuple[bool, str]:
        """Check if supplier is confirming the budget."""
        if not user or not budget:
            return False, "Usuário e orçamento são obrigatórios"
        
        if user != budget.fornecedor:
            return False, "Apenas o fornecedor pode confirmar o orçamento"
        
        if budget.status != 'aceito_pelo_cliente':
            return False, "Orçamento deve estar 'aceito_pelo_cliente' para ser confirmado"
        
        return True, ""
    
    def _condition_budget_refused_by_supplier(self, user=None, budget=None, **kwargs) -> Tuple[bool, str]:
        """Check if supplier is refusing the budget."""
        if not user or not budget:
            return False, "Usuário e orçamento são obrigatórios"
        
        if user != budget.fornecedor:
            return False, "Apenas o fornecedor pode recusar o orçamento"
        
        if budget.status != 'aceito_pelo_cliente':
            return False, "Orçamento deve estar 'aceito_pelo_cliente' para ser recusado"
        
        return True, ""
    
    def _condition_service_completed(self, user=None, **kwargs) -> Tuple[bool, str]:
        """Check if service can be marked as completed."""
        if not user:
            return False, "Usuário é obrigatório"
        
        if user != self.instance.cliente:
            return False, "Apenas o cliente pode finalizar a necessidade"
        
        # Check if there's a confirmed budget
        confirmed_budget = self.instance.orcamentos.filter(status='confirmado').first()
        if not confirmed_budget:
            return False, "Deve haver um orçamento confirmado para finalizar"
        
        return True, ""
    
    def _condition_can_open_dispute(self, user=None, disputa=None, **kwargs) -> Tuple[bool, str]:
        """Check if a dispute can be opened."""
        if not user:
            return False, "Usuário é obrigatório para abrir disputa"
        
        # Verificar se usuário é cliente ou fornecedor
        confirmed_budget = self.instance.orcamentos.filter(status='confirmado').first()
        if not confirmed_budget:
            return False, "Não há orçamento confirmado para abrir disputa"
        
        if user not in [self.instance.cliente, confirmed_budget.fornecedor]:
            return False, "Apenas cliente ou fornecedor podem abrir disputas"
        
        # Verificar se já existe disputa ativa
        active_disputes = self.instance.disputas.filter(status__in=['aberta', 'em_analise'])
        if active_disputes.exists():
            return False, "Já existe uma disputa ativa para esta necessidade"
        
        return True, ""
    
    def _condition_dispute_resolved_continue(self, user=None, disputa=None, **kwargs) -> Tuple[bool, str]:
        """Check if dispute resolution allows continuing service."""
        if not user or not user.is_staff:
            return False, "Apenas administradores podem resolver disputas"
        
        if not disputa or disputa.status != 'resolvida':
            return False, "Disputa deve estar resolvida"
        
        if disputa.status_final_necessidade != 'em_atendimento':
            return False, "Resolução da disputa não permite continuar atendimento"
        
        return True, ""
    
    def _condition_dispute_resolved_complete(self, user=None, disputa=None, **kwargs) -> Tuple[bool, str]:
        """Check if dispute resolution allows completing service."""
        if not user or not user.is_staff:
            return False, "Apenas administradores podem resolver disputas"
        
        if not disputa or disputa.status != 'resolvida':
            return False, "Disputa deve estar resolvida"
        
        if disputa.status_final_necessidade != 'finalizado':
            return False, "Resolução da disputa não permite finalizar necessidade"
        
        return True, ""
    
    def _condition_dispute_resolved_cancel(self, user=None, disputa=None, **kwargs) -> Tuple[bool, str]:
        """Check if dispute resolution allows cancelling service."""
        if not user or not user.is_staff:
            return False, "Apenas administradores podem resolver disputas"
        
        if not disputa or disputa.status != 'resolvida':
            return False, "Disputa deve estar resolvida"
        
        if disputa.status_final_necessidade != 'cancelado':
            return False, "Resolução da disputa não permite cancelar necessidade"
        
        return True, ""
    
    # Side Effects
    def _effect_first_budget_received(self, **kwargs):
        """Execute when first budget is received."""
        if not hasattr(self.instance, 'data_primeiro_orcamento'):
            # This field will be added in migration
            pass
        else:
            self.instance.data_primeiro_orcamento = timezone.now()
        
        self._send_notification('FIRST_BUDGET_RECEIVED')
    
    def _effect_budget_accepted(self, budget=None, **kwargs):
        """Execute when budget is accepted by client."""
        if budget:
            # Reject all other budgets
            self.instance.orcamentos.exclude(id=budget.id).update(status='rejeitado_pelo_cliente')
            
            # Update budget status
            budget.status = 'aceito_pelo_cliente'
            budget.save()
        
        if not hasattr(self.instance, 'aguardando_confirmacao_desde'):
            # This field will be added in migration
            pass
        else:
            self.instance.aguardando_confirmacao_desde = timezone.now()
        
        self._send_notification('BUDGET_ACCEPTED')
    
    def _effect_service_started(self, budget=None, **kwargs):
        """Execute when service starts."""
        if budget:
            budget.status = 'confirmado'
            budget.save()
        
        self._send_notification('SERVICE_STARTED')
    
    def _effect_budget_refused(self, budget=None, **kwargs):
        """Execute when supplier refuses budget."""
        if budget:
            budget.status = 'recusado_pelo_fornecedor'
            budget.save()
        
        # Clear aguardando_confirmacao_desde
        if hasattr(self.instance, 'aguardando_confirmacao_desde'):
            self.instance.aguardando_confirmacao_desde = None
        
        self._send_notification('BUDGET_REFUSED')
    
    def _effect_service_completed(self, **kwargs):
        """Execute when service is completed."""
        if not hasattr(self.instance, 'data_finalizacao'):
            # This field will be added in migration
            pass
        else:
            self.instance.data_finalizacao = timezone.now()
            
        if not hasattr(self.instance, 'avaliacao_liberada'):
            # This field will be added in migration
            pass
        else:
            self.instance.avaliacao_liberada = True
        
        self._send_notification('SERVICE_COMPLETED')
    
    def _effect_cancelled(self, **kwargs):
        """Execute when necessidade is cancelled."""
        # Update all pending budgets to anuncio_cancelado
        self.instance.orcamentos.filter(
            status__in=['enviado', 'aceito_pelo_cliente']
        ).update(status='anuncio_cancelado')
        
        self._send_notification('NECESSIDADE_CANCELLED')
    
    def _effect_dispute_opened(self, user=None, disputa=None, **kwargs):
        """Execute when a dispute is opened."""
        # Notificar a contraparte sobre a abertura da disputa
        confirmed_budget = self.instance.orcamentos.filter(status='confirmado').first()
        if confirmed_budget:
            if user == self.instance.cliente:
                # Cliente abriu disputa, notificar fornecedor
                target_user = confirmed_budget.fornecedor
                message = f'O cliente abriu uma disputa sobre o serviço "{self.instance.titulo}".'
            else:
                # Fornecedor abriu disputa, notificar cliente
                target_user = self.instance.cliente
                message = f'O fornecedor abriu uma disputa sobre o serviço "{self.instance.titulo}".'
            
            self._send_notification_to_user(target_user, 'DISPUTE_OPENED', message)
        
        # Notificar administradores
        self._notify_admins_new_dispute(disputa)
    
    def _effect_dispute_resolved_continue(self, user=None, disputa=None, **kwargs):
        """Execute when dispute is resolved and service continues."""
        self._send_notification('DISPUTE_RESOLVED_CONTINUE')
    
    def _effect_dispute_resolved_complete(self, user=None, disputa=None, **kwargs):
        """Execute when dispute is resolved and service is completed."""
        # Marcar avaliação como liberada
        if hasattr(self.instance, 'avaliacao_liberada'):
            self.instance.avaliacao_liberada = True
        
        self._send_notification('DISPUTE_RESOLVED_COMPLETE')
    
    def _effect_dispute_resolved_cancel(self, user=None, disputa=None, **kwargs):
        """Execute when dispute is resolved and service is cancelled."""
        # Cancelar orçamentos relacionados
        self.instance.orcamentos.filter(
            status__in=['confirmado']
        ).update(status='anuncio_cancelado')
        
        self._send_notification('DISPUTE_RESOLVED_CANCEL')
    
    def _send_notification(self, notification_type: str):
        """Send notification for state transition."""
        try:
            from notifications.models import Notification, NotificationType
            
            type_mapping = {
                'FIRST_BUDGET_RECEIVED': NotificationType.NEW_BUDGET,
                'BUDGET_ACCEPTED': NotificationType.NEW_BUDGET,
                'SERVICE_STARTED': NotificationType.NEW_BUDGET,
                'BUDGET_REFUSED': NotificationType.NEW_BUDGET,
                'SERVICE_COMPLETED': NotificationType.NEW_END_AD,
                'NECESSIDADE_CANCELLED': NotificationType.NEW_END_AD,
                'DISPUTE_OPENED': NotificationType.SYSTEM_MESSAGE,
                'DISPUTE_RESOLVED_CONTINUE': NotificationType.SYSTEM_MESSAGE,
                'DISPUTE_RESOLVED_COMPLETE': NotificationType.NEW_END_AD,
                'DISPUTE_RESOLVED_CANCEL': NotificationType.NEW_END_AD,
            }
            
            if notification_type in type_mapping:
                Notification.objects.create(
                    user=self.instance.cliente,
                    message=f"Status da necessidade '{self.instance.titulo}' foi atualizado.",
                    notification_type=type_mapping[notification_type],
                    necessidade=self.instance
                )
        except ImportError:
            logger.warning("Notification system not available")
    
    def _send_notification_to_user(self, user, notification_type: str, message: str):
        """Send notification to a specific user."""
        try:
            from notifications.models import Notification, NotificationType
            
            type_mapping = {
                'DISPUTE_OPENED': NotificationType.SYSTEM_MESSAGE,
            }
            
            Notification.objects.create(
                user=user,
                title='Nova Disputa',
                message=message,
                notification_type=type_mapping.get(notification_type, NotificationType.SYSTEM_MESSAGE),
                necessidade=self.instance
            )
        except ImportError:
            logger.warning("Notification system not available")
    
    def _notify_admins_new_dispute(self, disputa=None):
        """Notify administrators about new dispute."""
        try:
            from notifications.models import Notification, NotificationType
            from django.contrib.auth import get_user_model
            
            User = get_user_model()
            admins = User.objects.filter(is_staff=True)
            
            for admin in admins:
                Notification.objects.create(
                    user=admin,
                    title='Nova Disputa Requer Atenção',
                    message=f'Uma nova disputa foi aberta para "{self.instance.titulo}" e requer análise administrativa.',
                    notification_type=NotificationType.SYSTEM_MESSAGE,
                    necessidade=self.instance,
                    metadata={'disputa_id': disputa.pk if disputa else None, 'urgente': True}
                )
        except ImportError:
            logger.warning("Notification system not available")
    
    def _update_timestamps(self, old_state: str, new_state: str):
        """Update specific timestamp fields."""
        super()._update_timestamps(old_state, new_state)
        
        now = timezone.now()
        
        # Update specific timestamps based on transitions
        if old_state == 'ativo' and new_state == 'analisando_orcamentos':
            if hasattr(self.instance, 'data_primeiro_orcamento'):
                self.instance.data_primeiro_orcamento = now
        
        elif old_state == 'analisando_orcamentos' and new_state == 'aguardando_confirmacao':
            if hasattr(self.instance, 'aguardando_confirmacao_desde'):
                self.instance.aguardando_confirmacao_desde = now
        
        elif new_state == 'finalizado':
            if hasattr(self.instance, 'data_finalizacao'):
                self.instance.data_finalizacao = now
                
            if hasattr(self.instance, 'avaliacao_liberada'):
                self.instance.avaliacao_liberada = True
    
    def is_confirmation_expired(self) -> bool:
        """Check if confirmation timeout has expired."""
        if (self.get_current_state() == 'aguardando_confirmacao' and 
            hasattr(self.instance, 'aguardando_confirmacao_desde') and
            self.instance.aguardando_confirmacao_desde):
            
            timeout_time = self.instance.aguardando_confirmacao_desde + timedelta(hours=self.CONFIRMATION_TIMEOUT)
            return timezone.now() > timeout_time
        
        return False
    
    def handle_timeout(self) -> bool:
        """Handle confirmation timeout automatically."""
        if self.is_confirmation_expired():
            try:
                # Transition back to analisando_orcamentos
                self.transition_to('analisando_orcamentos')
                
                # Reset the accepted budget to enviado
                accepted_budget = self.instance.orcamentos.filter(status='aceito_pelo_cliente').first()
                if accepted_budget:
                    accepted_budget.status = 'enviado'
                    accepted_budget.save()
                
                logger.info(f"Confirmation timeout handled for necessidade {self.instance.id}")
                return True
                
            except StateTransitionError as e:
                logger.error(f"Failed to handle timeout for necessidade {self.instance.id}: {e}")
                return False
        
        return False


class OrcamentoStateMachine(StateMachineBase):
    """
    State machine for Orçamento model.
    """
    
    def _setup_transitions(self):
        """Define valid state transitions for Orçamento."""
        # From enviado
        self.add_transition('enviado', 'aceito_pelo_cliente')
        self.add_transition('enviado', 'rejeitado_pelo_cliente')
        self.add_transition('enviado', 'cancelado_pelo_fornecedor')
        self.add_transition('enviado', 'anuncio_cancelado')
        self.add_transition('enviado', 'anuncio_expirado')
        
        # From aceito_pelo_cliente
        self.add_transition('aceito_pelo_cliente', 'confirmado')
        self.add_transition('aceito_pelo_cliente', 'recusado_pelo_fornecedor')
        self.add_transition('aceito_pelo_cliente', 'anuncio_cancelado')
        self.add_transition('aceito_pelo_cliente', 'anuncio_expirado')
        
        # From confirmado
        self.add_transition('confirmado', 'finalizado')
        self.add_transition('confirmado', 'anuncio_cancelado')
        
        # Status terminais (não têm transições de saída)
        # rejeitado_pelo_cliente, recusado_pelo_fornecedor, cancelado_pelo_fornecedor, 
        # finalizado, anuncio_cancelado, anuncio_expirado são estados finais
    
    def _setup_conditions(self):
        """Define transition conditions."""
        self.conditions[('enviado', 'aceito_pelo_cliente')] = self._condition_client_accepts
        self.conditions[('enviado', 'rejeitado_pelo_cliente')] = self._condition_client_rejects
        self.conditions[('aceito_pelo_cliente', 'confirmado')] = self._condition_supplier_confirms
        self.conditions[('aceito_pelo_cliente', 'recusado_pelo_fornecedor')] = self._condition_supplier_refuses
    
    def _setup_side_effects(self):
        """Define side effects for transitions."""
        self.side_effects[('enviado', 'aceito_pelo_cliente')] = self._effect_accepted_by_client
        self.side_effects[('aceito_pelo_cliente', 'confirmado')] = self._effect_confirmed_by_supplier
        self.side_effects[('aceito_pelo_cliente', 'recusado_pelo_fornecedor')] = self._effect_refused_by_supplier
    
    # Conditions
    def _condition_client_accepts(self, user=None, **kwargs) -> Tuple[bool, str]:
        """Check if client can accept this budget."""
        if not user:
            return False, "Usuário é obrigatório"
        
        if user != self.instance.anuncio.cliente:
            return False, "Apenas o cliente pode aceitar orçamentos"
        
        # Check if necessidade is in correct state
        if self.instance.anuncio.status not in ['ativo', 'analisando_orcamentos']:
            return False, "A necessidade deve estar ativa ou analisando orçamentos"
        
        return True, ""
    
    def _condition_client_rejects(self, user=None, **kwargs) -> Tuple[bool, str]:
        """Check if client can reject this budget."""
        if not user:
            return False, "Usuário é obrigatório"
        
        if user != self.instance.anuncio.cliente:
            return False, "Apenas o cliente pode rejeitar orçamentos"
        
        return True, ""
    
    def _condition_supplier_confirms(self, user=None, **kwargs) -> Tuple[bool, str]:
        """Check if supplier can confirm this budget."""
        if not user:
            return False, "Usuário é obrigatório"
        
        if user != self.instance.fornecedor:
            return False, "Apenas o fornecedor pode confirmar orçamentos"
        
        return True, ""
    
    def _condition_supplier_refuses(self, user=None, **kwargs) -> Tuple[bool, str]:
        """Check if supplier can refuse this budget."""
        if not user:
            return False, "Usuário é obrigatório"
        
        if user != self.instance.fornecedor:
            return False, "Apenas o fornecedor pode recusar orçamentos"
        
        return True, ""
    
    # Side Effects
    def _effect_accepted_by_client(self, user=None, **kwargs):
        """Execute when client accepts budget."""
        # Update necessidade state using its state machine
        necessidade_sm = NecessidadeStateMachine(self.instance.anuncio)
        try:
            necessidade_sm.transition_to('aguardando_confirmacao', user=user, budget=self.instance)
        except StateTransitionError as e:
            logger.error(f"Failed to update necessidade state when budget accepted: {e}")
        
        self._send_notification('BUDGET_ACCEPTED_BY_CLIENT')
    
    def _effect_confirmed_by_supplier(self, user=None, **kwargs):
        """Execute when supplier confirms budget."""
        # Update necessidade state
        necessidade_sm = NecessidadeStateMachine(self.instance.anuncio)
        try:
            necessidade_sm.transition_to('em_atendimento', user=user, budget=self.instance)
        except StateTransitionError as e:
            logger.error(f"Failed to update necessidade state when budget confirmed: {e}")
        
        self._send_notification('BUDGET_CONFIRMED_BY_SUPPLIER')
    
    def _effect_refused_by_supplier(self, user=None, **kwargs):
        """Execute when supplier refuses budget."""
        # Update necessidade state back to analisando_orcamentos
        necessidade_sm = NecessidadeStateMachine(self.instance.anuncio)
        try:
            necessidade_sm.transition_to('analisando_orcamentos', user=user, budget=self.instance)
        except StateTransitionError as e:
            logger.error(f"Failed to update necessidade state when budget refused: {e}")
        
        self._send_notification('BUDGET_REFUSED_BY_SUPPLIER')
    
    def _send_notification(self, notification_type: str):
        """Send notification for budget state transition."""
        try:
            from notifications.models import Notification, NotificationType
            
            # Notify the relevant user based on the transition
            if notification_type == 'BUDGET_ACCEPTED_BY_CLIENT':
                # Notify supplier
                user_to_notify = self.instance.fornecedor
                message = f"Seu orçamento para '{self.instance.anuncio.titulo}' foi aceito pelo cliente."
            elif notification_type == 'BUDGET_CONFIRMED_BY_SUPPLIER':
                # Notify client
                user_to_notify = self.instance.anuncio.cliente
                message = f"Orçamento para '{self.instance.anuncio.titulo}' foi confirmado pelo fornecedor."
            elif notification_type == 'BUDGET_REFUSED_BY_SUPPLIER':
                # Notify client
                user_to_notify = self.instance.anuncio.cliente
                message = f"Orçamento para '{self.instance.anuncio.titulo}' foi recusado pelo fornecedor."
            else:
                return
            
            Notification.objects.create(
                user=user_to_notify,
                message=message,
                notification_type=NotificationType.NEW_BUDGET,
                necessidade=self.instance.anuncio
            )
        except ImportError:
            logger.warning("Notification system not available")


# Factory functions for easy access
def get_necessidade_state_machine(necessidade):
    """Get state machine instance for a Necessidade."""
    return NecessidadeStateMachine(necessidade)


def get_orcamento_state_machine(orcamento):
    """Get state machine instance for an Orçamento."""
    return OrcamentoStateMachine(orcamento)