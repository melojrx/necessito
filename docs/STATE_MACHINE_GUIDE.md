# State Machine Implementation Guide

## Overview

This document describes the comprehensive State Machine implementation for Necessidade and Orçamento models in the Indicai marketplace platform. The state machine ensures proper business rule compliance, automatic transitions, and robust data integrity.

## Architecture

### Core Components

1. **`core/state_machine.py`** - Main state machine classes
2. **`core/state_machine/transitions.py`** - Transition definitions and business rules
3. **`ads/models.py`** - Enhanced Necessidade model with state machine integration
4. **`budgets/models.py`** - Enhanced Orçamento model with state machine integration
5. **`core/permissions.py`** - Updated permissions using state machine logic
6. **`ads/tasks.py`** - Celery tasks for automatic timeout handling
7. **`ads/management/commands/handle_timeouts.py`** - Management command for timeout handling

### Key Features

- **Transaction Safety**: All state transitions are atomic
- **Business Rule Enforcement**: Comprehensive validation before transitions
- **Automatic Timeout Handling**: 48-hour timeout for confirmation status
- **Audit Trail**: Timestamp tracking for all state changes
- **Notification Integration**: Automatic notifications on state changes
- **Permission Integration**: Role-based access control for transitions
- **Backwards Compatibility**: Works with existing data

## State Definitions

### Necessidade States

| Status | Description | Valid Transitions |
|--------|-------------|-------------------|
| `ativo` | Necessidade ativa aguardando orçamentos | `analisando_orcamentos`, `cancelado`, `expirado` |
| `analisando_orcamentos` | Cliente analisando orçamentos recebidos | `aguardando_confirmacao`, `cancelado`, `expirado` |
| `aguardando_confirmacao` | Aguardando confirmação do fornecedor (48h timeout) | `em_atendimento`, `analisando_orcamentos`, `cancelado`, `expirado` |
| `em_atendimento` | Serviço em execução | `finalizado`, `cancelado` |
| `finalizado` | Necessidade finalizada (terminal) | None |
| `cancelado` | Necessidade cancelada (terminal) | None |
| `expirado` | Necessidade expirada automaticamente (terminal) | None |

### Orçamento States

| Status | Description | Valid Transitions |
|--------|-------------|-------------------|
| `enviado` | Orçamento enviado aguardando resposta | `aceito_pelo_cliente`, `rejeitado_pelo_cliente`, `cancelado` |
| `aceito_pelo_cliente` | Aceito pelo cliente, aguardando fornecedor | `confirmado`, `recusado_pelo_fornecedor`, `cancelado` |
| `confirmado` | Confirmado - serviço em execução | `cancelado` |
| `rejeitado_pelo_cliente` | Rejeitado pelo cliente | `cancelado` |
| `recusado_pelo_fornecedor` | Recusado pelo fornecedor | `cancelado` |
| `cancelado` | Orçamento cancelado (terminal) | None |

## Business Rules

### Necessidade Rules

1. **First Budget Transition**: `ativo` → `analisando_orcamentos`
   - Triggered when first budget is received
   - Updates `data_primeiro_orcamento` timestamp

2. **Budget Acceptance**: `analisando_orcamentos` → `aguardando_confirmacao`
   - Only client can trigger
   - All other budgets are automatically rejected
   - Sets `aguardando_confirmacao_desde` timestamp
   - 48-hour timeout starts

3. **Service Start**: `aguardando_confirmacao` → `em_atendimento`
   - Only supplier can trigger
   - Must be the supplier of accepted budget

4. **Timeout Handling**: `aguardando_confirmacao` → `analisando_orcamentos`
   - Automatic after 48 hours
   - Budget returns to `enviado` status
   - Notifications sent to all parties

5. **Service Completion**: `em_atendimento` → `finalizado`
   - Only client can trigger
   - Sets `data_finalizacao` timestamp
   - Enables evaluation (`avaliacao_liberada = True`)

6. **Cancellation**: Any status → `cancelado`
   - Only client can trigger
   - All pending budgets are cancelled

### Orçamento Rules

1. **Client Acceptance**: `enviado` → `aceito_pelo_cliente`
   - Only client can trigger
   - Other budgets for same necessidade are rejected

2. **Supplier Confirmation**: `aceito_pelo_cliente` → `confirmado`
   - Only supplier can trigger
   - Necessidade transitions to `em_atendimento`

3. **Supplier Refusal**: `aceito_pelo_cliente` → `recusado_pelo_fornecedor`
   - Only supplier can trigger
   - Necessidade returns to `analisando_orcamentos`

## Usage Examples

### Basic Usage

```python
from ads.models import Necessidade
from budgets.models import Orcamento

# Get necessidade and check valid transitions
necessidade = Necessidade.objects.get(id=1)
valid_transitions = necessidade.get_valid_transitions()

# Check if transition is allowed
can_transition, message = necessidade.can_transition_to('finalizado', user=request.user)

# Execute transition
if can_transition:
    necessidade.transition_to('finalizado', user=request.user)
```

### With Orçamento

```python
# Accept budget
budget = Orcamento.objects.get(id=1)
if budget.can_be_accepted(user=request.user):
    budget.transition_to('aceito_pelo_cliente', user=request.user)

# Confirm budget
if budget.can_be_confirmed(user=request.user):
    budget.transition_to('confirmado', user=request.user)
```

### Permission Checking

```python
from core.permissions import PermissionValidator

# Check if user can accept budget
can_accept, message = PermissionValidator.can_accept_budget(request.user, budget)

# Check if user can finalize necessidade
can_finalize, message = PermissionValidator.can_finalize_ad(request.user, necessidade)
```

## Automatic Timeout Management

### Celery Tasks

Add to your `CELERY_BEAT_SCHEDULE`:

```python
CELERY_BEAT_SCHEDULE = {
    'handle-confirmation-timeouts': {
        'task': 'ads.tasks.handle_confirmation_timeouts',
        'schedule': crontab(minute=0),  # Every hour
    },
    'send-timeout-notifications': {
        'task': 'ads.tasks.send_timeout_notifications',
        'schedule': crontab(minute=0, hour='*/6'),  # Every 6 hours
    },
    'cleanup-expired-necessidades': {
        'task': 'ads.tasks.cleanup_expired_necessidades',
        'schedule': crontab(minute=0, hour=2),  # Daily at 2 AM
    },
}
```

### Management Command

```bash
# Handle timeouts manually
python manage.py handle_timeouts

# Dry run to see what would be processed
python manage.py handle_timeouts --dry-run

# Verbose output
python manage.py handle_timeouts --verbose
```

## Database Migration

The implementation adds new timestamp fields to the Necessidade model:

```sql
-- New fields added
ALTER TABLE ads_necessidade ADD COLUMN data_primeiro_orcamento TIMESTAMP NULL;
ALTER TABLE ads_necessidade ADD COLUMN aguardando_confirmacao_desde TIMESTAMP NULL;
ALTER TABLE ads_necessidade ADD COLUMN data_finalizacao TIMESTAMP NULL;
ALTER TABLE ads_necessidade ADD COLUMN avaliacao_liberada BOOLEAN DEFAULT FALSE;
```

Apply migration:
```bash
python manage.py migrate ads
```

## Testing

### Unit Tests

Run the provided test script:
```bash
python test_state_machine.py
```

### Manual Testing

1. Create a necessidade
2. Create orçamentos
3. Accept an orçamento (client action)
4. Confirm orçamento (supplier action)
5. Finalize necessidade (client action)
6. Test timeout scenarios

## Error Handling

### StateTransitionError

```python
from core.state_machine import StateTransitionError

try:
    necessidade.transition_to('invalid_status', user=user)
except StateTransitionError as e:
    # Handle transition error
    messages.error(request, str(e))
```

### Transaction Rollback

All state transitions are wrapped in database transactions. If any part fails, the entire operation is rolled back.

## Monitoring

### Logs

State machine operations are logged with the following format:
```
INFO: State transition successful: ativo -> analisando_orcamentos for Necessidade 123
ERROR: State transition failed: aguardando_confirmacao -> finalizado for Necessidade 123. Error: Invalid transition
```

### Metrics

Track these metrics in your monitoring system:
- Number of timeout events per day
- Average time in each status
- Failed transition attempts
- Notification delivery success rate

## Integration Points

### Views

Update your views to use state machine methods:

```python
# Instead of manual status updates
necessidade.status = 'finalizado'
necessidade.save()

# Use state machine
necessidade.transition_to('finalizado', user=request.user)
```

### API

For API endpoints, use the state machine for validation:

```python
@api_view(['POST'])
def accept_budget(request, budget_id):
    budget = get_object_or_404(Orcamento, id=budget_id)
    
    can_accept, message = budget.can_transition_to('aceito_pelo_cliente', user=request.user)
    if not can_accept:
        return Response({'error': message}, status=400)
    
    budget.transition_to('aceito_pelo_cliente', user=request.user)
    return Response({'status': 'success'})
```

## Troubleshooting

### Common Issues

1. **ImportError on state machine**: Ensure all imports are correct and Django is properly set up
2. **Timeout not working**: Check that Celery is running and beat schedule is configured
3. **Notifications not sent**: Verify notification system is available and properly imported
4. **Permission denied**: Check user roles and state machine conditions

### Debug Mode

Enable debug logging:
```python
LOGGING = {
    'loggers': {
        'core.state_machine': {
            'level': 'DEBUG',
            'handlers': ['console'],
        },
    },
}
```

## Performance Considerations

1. **Database Queries**: State machine operations are optimized to minimize queries
2. **Caching**: Consider caching valid transitions for frequently accessed objects
3. **Bulk Operations**: For bulk status updates, use queryset updates where appropriate
4. **Timeout Processing**: Monitor timeout task performance and adjust frequency as needed

## Security

1. **Permission Validation**: Always validate user permissions before transitions
2. **Input Validation**: State machine validates all inputs and conditions
3. **Audit Trail**: All transitions are logged with user information
4. **Transaction Safety**: Atomic operations prevent data corruption

## Future Enhancements

1. **State Transition History**: Add model to track all state changes
2. **Custom Timeout Periods**: Allow per-necessidade timeout configuration
3. **Workflow Templates**: Define common transition patterns
4. **Analytics Dashboard**: Visual representation of state flows
5. **Webhook Integration**: External system notifications on state changes