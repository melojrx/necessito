"""
Celery tasks for handling state machine operations and timeouts.
"""

from celery import shared_task
from django.utils import timezone
from datetime import timedelta
import logging

from ads.models import Necessidade
from core.state_machine import StateTransitionError

logger = logging.getLogger(__name__)


@shared_task(bind=True)
def handle_confirmation_timeouts(self):
    """
    Handle confirmation timeouts for necessidades.
    This task should be run periodically (e.g., every hour).
    """
    try:
        # Find necessidades that might have expired confirmation
        expired_candidates = Necessidade.objects.filter(
            status='aguardando_confirmacao',
            aguardando_confirmacao_desde__isnull=False,
            aguardando_confirmacao_desde__lt=timezone.now() - timedelta(hours=48)
        )

        processed_count = 0
        error_count = 0

        for necessidade in expired_candidates:
            try:
                if necessidade.is_confirmation_expired():
                    success = necessidade.handle_timeout()
                    if success:
                        processed_count += 1
                        logger.info(f"Handled timeout for necessidade {necessidade.id}")
                    else:
                        error_count += 1
                        logger.error(f"Failed to handle timeout for necessidade {necessidade.id}")
            except Exception as e:
                error_count += 1
                logger.error(f"Error processing timeout for necessidade {necessidade.id}: {str(e)}")

        logger.info(f"Timeout handler completed. Processed: {processed_count}, Errors: {error_count}")
        
        return {
            'status': 'completed',
            'processed': processed_count,
            'errors': error_count,
            'total_checked': expired_candidates.count()
        }

    except Exception as e:
        logger.error(f"Critical error in handle_confirmation_timeouts: {str(e)}")
        self.retry(countdown=300, max_retries=3)  # Retry after 5 minutes, max 3 times


@shared_task(bind=True)
def transition_necessidade_status(self, necessidade_id, new_status, user_id=None, **kwargs):
    """
    Async task to handle necessidade status transitions.
    Useful for complex transitions that might take time or need to be queued.
    """
    try:
        from django.contrib.auth import get_user_model
        
        User = get_user_model()
        necessidade = Necessidade.objects.get(id=necessidade_id)
        user = User.objects.get(id=user_id) if user_id else None

        old_status = necessidade.status
        necessidade.transition_to(new_status, user=user, **kwargs)

        logger.info(f"Successfully transitioned necessidade {necessidade_id} from {old_status} to {new_status}")
        
        return {
            'status': 'success',
            'necessidade_id': necessidade_id,
            'old_status': old_status,
            'new_status': new_status
        }

    except Necessidade.DoesNotExist:
        logger.error(f"Necessidade {necessidade_id} not found")
        return {'status': 'error', 'message': 'Necessidade not found'}
    
    except StateTransitionError as e:
        logger.error(f"State transition error for necessidade {necessidade_id}: {str(e)}")
        return {'status': 'error', 'message': str(e)}
    
    except Exception as e:
        logger.error(f"Unexpected error in transition_necessidade_status: {str(e)}")
        self.retry(countdown=60, max_retries=3)


@shared_task(bind=True)
def transition_orcamento_status(self, orcamento_id, new_status, user_id=None, **kwargs):
    """
    Async task to handle orçamento status transitions.
    """
    try:
        from django.contrib.auth import get_user_model
        from budgets.models import Orcamento
        
        User = get_user_model()
        orcamento = Orcamento.objects.get(id=orcamento_id)
        user = User.objects.get(id=user_id) if user_id else None

        old_status = orcamento.status
        orcamento.transition_to(new_status, user=user, **kwargs)

        logger.info(f"Successfully transitioned orcamento {orcamento_id} from {old_status} to {new_status}")
        
        return {
            'status': 'success',
            'orcamento_id': orcamento_id,
            'old_status': old_status,
            'new_status': new_status
        }

    except Exception as e:
        logger.error(f"Error in transition_orcamento_status: {str(e)}")
        return {'status': 'error', 'message': str(e)}


@shared_task
def send_timeout_notifications():
    """
    Send notifications for necessidades approaching timeout.
    Run this task more frequently (e.g., every 6 hours) to warn users.
    """
    try:
        # Find necessidades that will expire in the next 12 hours
        warning_time = timezone.now() - timedelta(hours=36)  # 48h - 12h = 36h ago
        
        approaching_timeout = Necessidade.objects.filter(
            status='aguardando_confirmacao',
            aguardando_confirmacao_desde__isnull=False,
            aguardando_confirmacao_desde__lt=warning_time,
            aguardando_confirmacao_desde__gte=timezone.now() - timedelta(hours=48)
        )

        notification_count = 0

        for necessidade in approaching_timeout:
            try:
                # Send notification to supplier
                accepted_budget = necessidade.get_accepted_budget()
                if accepted_budget:
                    from notifications.models import Notification, NotificationType
                    
                    # Check if we already sent a warning
                    existing_warning = Notification.objects.filter(
                        user=accepted_budget.fornecedor,
                        necessidade=necessidade,
                        message__contains='expirará em breve',
                        created_at__gte=timezone.now() - timedelta(hours=24)
                    ).exists()

                    if not existing_warning:
                        Notification.objects.create(
                            user=accepted_budget.fornecedor,
                            message=f"ATENÇÃO: O orçamento para '{necessidade.titulo}' expirará em breve. Confirme ou recuse até {necessidade.aguardando_confirmacao_desde + timedelta(hours=48)}.",
                            notification_type=NotificationType.NEW_BUDGET,
                            necessidade=necessidade
                        )
                        notification_count += 1

            except Exception as e:
                logger.error(f"Error sending timeout notification for necessidade {necessidade.id}: {str(e)}")

        logger.info(f"Sent {notification_count} timeout warning notifications")
        return {'status': 'completed', 'notifications_sent': notification_count}

    except Exception as e:
        logger.error(f"Error in send_timeout_notifications: {str(e)}")
        return {'status': 'error', 'message': str(e)}


@shared_task
def cleanup_expired_necessidades():
    """
    Clean up very old necessidades by marking them as expired.
    This is a maintenance task that should run daily.
    """
    try:
        # Mark very old active necessidades as expired (e.g., 60 days)
        expiration_date = timezone.now() - timedelta(days=60)
        
        old_active = Necessidade.objects.filter(
            status='ativo',
            data_criacao__lt=expiration_date
        )

        expired_count = 0
        for necessidade in old_active:
            try:
                necessidade.transition_to('expirado')
                expired_count += 1
            except StateTransitionError as e:
                logger.warning(f"Could not expire necessidade {necessidade.id}: {str(e)}")

        logger.info(f"Expired {expired_count} old necessidades")
        return {'status': 'completed', 'expired_count': expired_count}

    except Exception as e:
        logger.error(f"Error in cleanup_expired_necessidades: {str(e)}")
        return {'status': 'error', 'message': str(e)}


@shared_task
def verificar_anuncios_expirados():
    """
    Verifica e expira anúncios que passaram da data de validade.
    Deve ser executado diariamente via Celery Beat.
    """
    try:
        from notifications.models import Notification, NotificationType
        
        # Buscar anúncios que devem expirar baseado em data_validade
        anuncios_para_expirar = Necessidade.objects.filter(
            status__in=['ativo', 'analisando_orcamentos', 'aguardando_confirmacao'],
            data_validade__lt=timezone.now()
        )
        
        contador = 0
        for anuncio in anuncios_para_expirar:
            try:
                # Atualizar status do anúncio usando state machine
                from core.state_machine import get_necessidade_state_machine
                state_machine = get_necessidade_state_machine(anuncio)
                state_machine.transition_to('expirado')
                
                # Atualizar status dos orçamentos relacionados
                from budgets.models import Orcamento
                anuncio.orcamentos.filter(
                    status__in=['enviado', 'aceito_pelo_cliente']
                ).update(status='anuncio_expirado')
                
                # Notificar o cliente
                Notification.objects.create(
                    user=anuncio.cliente,
                    message=f'Seu anúncio "{anuncio.titulo}" expirou sem fechar negócio.',
                    notification_type=NotificationType.NEW_END_AD,
                    necessidade=anuncio
                )
                
                # Notificar fornecedores que tinham orçamentos enviados
                fornecedores_notificados = set()
                for orcamento in anuncio.orcamentos.filter(status='anuncio_expirado'):
                    if orcamento.fornecedor not in fornecedores_notificados:
                        Notification.objects.create(
                            user=orcamento.fornecedor,
                            message=f'O anúncio "{anuncio.titulo}" expirou.',
                            notification_type=NotificationType.NEW_END_AD,
                            necessidade=anuncio
                        )
                        fornecedores_notificados.add(orcamento.fornecedor)
                
                contador += 1
                logger.info(f"Anúncio {anuncio.id} - {anuncio.titulo} expirado com sucesso")
                
            except Exception as e:
                logger.error(f"Erro ao expirar anúncio {anuncio.id}: {str(e)}")
                continue
        
        logger.info(f"Task verificar_anuncios_expirados concluída. {contador} anúncios expirados.")
        return {'status': 'completed', 'expired_count': contador}
        
    except Exception as e:
        logger.error(f"Erro na task verificar_anuncios_expirados: {str(e)}")
        return {'status': 'error', 'message': str(e)}