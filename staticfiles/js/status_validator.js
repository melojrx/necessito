/**
 * Status Validator - Validações do lado cliente para ações baseadas no status
 */
class StatusValidator {
  constructor(necessidadeId, currentStatus, userType, userId, clienteId) {
    this.necessidadeId = necessidadeId;
    this.currentStatus = currentStatus;
    this.userType = userType; // 'cliente', 'fornecedor', 'visitante'
    this.userId = userId;
    this.clienteId = clienteId;
    
    this.statusRules = {
      'ativo': {
        cliente: ['editar', 'cancelar'],
        fornecedor: ['enviar_orcamento'],
        visitante: []
      },
      'analisando_orcamentos': {
        cliente: ['cancelar', 'aceitar_orcamento', 'rejeitar_orcamento'],
        fornecedor: ['enviar_orcamento'], // ainda pode enviar se não enviou
        visitante: []
      },
      'aguardando_confirmacao': {
        cliente: ['cancelar', 'conversar'],
        fornecedor: ['confirmar_orcamento', 'rejeitar_orcamento', 'conversar'], // apenas o fornecedor aceito
        visitante: []
      },
      'em_atendimento': {
        cliente: ['finalizar', 'conversar'],
        fornecedor: ['conversar'], // apenas o fornecedor em atendimento
        visitante: []
      },
      'finalizado': {
        cliente: ['avaliar', 'ver_historico'],
        fornecedor: ['avaliar', 'ver_historico'], // apenas o fornecedor que executou
        visitante: []
      },
      'cancelado': {
        cliente: ['ver_historico'],
        fornecedor: ['ver_historico'],
        visitante: []
      }
    };
    
    this.init();
  }
  
  init() {
    this.setupEventListeners();
    this.validateCurrentState();
    this.setupTooltips();
  }
  
  /**
   * Verifica se uma ação é permitida para o usuário atual
   */
  canPerformAction(action) {
    const allowedActions = this.statusRules[this.currentStatus]?.[this.userType] || [];
    return allowedActions.includes(action);
  }
  
  /**
   * Valida se o usuário pode editar baseado no status
   */
  canEdit() {
    if (this.userType !== 'cliente') return false;
    return ['ativo'].includes(this.currentStatus);
  }
  
  /**
   * Valida se o usuário pode cancelar baseado no status
   */
  canCancel() {
    if (this.userType !== 'cliente') return false;
    return !['finalizado', 'cancelado'].includes(this.currentStatus);
  }
  
  /**
   * Valida se fornecedor pode enviar orçamento
   */
  canSubmitBudget() {
    if (this.userType !== 'fornecedor') return false;
    return ['ativo', 'analisando_orcamentos'].includes(this.currentStatus);
  }
  
  /**
   * Valida se pode finalizar serviço
   */
  canFinalize() {
    if (this.userType !== 'cliente') return false;
    return this.currentStatus === 'em_atendimento';
  }
  
  /**
   * Configura listeners para validações em tempo real
   */
  setupEventListeners() {
    // Validar botões de editar
    const editButtons = document.querySelectorAll('[data-action="edit"]');
    editButtons.forEach(btn => {
      if (!this.canEdit()) {
        this.disableButton(btn, 'Não é possível editar após receber orçamentos');
      }
    });
    
    // Validar botões de cancelar
    const cancelButtons = document.querySelectorAll('[data-action="cancel"]');
    cancelButtons.forEach(btn => {
      if (!this.canCancel()) {
        this.disableButton(btn, 'Não é possível cancelar anúncios finalizados');
      }
    });
    
    // Validar botões de orçamento
    const budgetButtons = document.querySelectorAll('[data-action="submit-budget"]');
    budgetButtons.forEach(btn => {
      if (!this.canSubmitBudget()) {
        this.disableButton(btn, 'Não é possível enviar orçamentos neste status');
      }
    });
    
    // Validar botões de finalizar
    const finalizeButtons = document.querySelectorAll('[data-action="finalize"]');
    finalizeButtons.forEach(btn => {
      if (!this.canFinalize()) {
        this.disableButton(btn, 'Só é possível finalizar serviços em atendimento');
      }
    });
  }
  
  /**
   * Desabilita um botão e adiciona tooltip explicativo
   */
  disableButton(button, reason) {
    button.disabled = true;
    button.classList.add('disabled');
    button.setAttribute('title', reason);
    button.setAttribute('data-bs-toggle', 'tooltip');
    
    // Adiciona ícone de aviso
    const icon = button.querySelector('i');
    if (icon) {
      icon.classList.add('text-muted');
    }
  }
  
  /**
   * Valida o estado atual da página
   */
  validateCurrentState() {
    const container = document.querySelector(`[data-status="${this.currentStatus}"]`);
    if (container) {
      container.classList.add('status-validated');
    }
    
    // Adiciona classes CSS baseadas no tipo de usuário
    document.body.classList.add(`user-type-${this.userType}`);
    document.body.classList.add(`status-${this.currentStatus}`);
  }
  
  /**
   * Configura tooltips informativos
   */
  setupTooltips() {
    // Inicializar todos os tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
      return new bootstrap.Tooltip(tooltipTriggerEl);
    });
  }
  
  /**
   * Mostra notificação sobre regras de negócio
   */
  showBusinessRuleInfo(action) {
    const rules = {
      'edit_blocked': {
        title: 'Edição Bloqueada',
        message: 'Você não pode mais editar este anúncio pois já recebeu orçamentos. Isso garante transparência na negociação.',
        type: 'warning'
      },
      'budget_closed': {
        title: 'Orçamentos Fechados',
        message: 'Este anúncio não está mais aceitando novos orçamentos.',
        type: 'info'
      },
      'awaiting_confirmation': {
        title: 'Aguardando Confirmação',
        message: 'Um orçamento foi aceito e está aguardando confirmação do fornecedor (prazo: 48h).',
        type: 'info'
      }
    };
    
    const rule = rules[action];
    if (rule) {
      this.showAlert(rule.title, rule.message, rule.type);
    }
  }
  
  /**
   * Mostra alerta na interface
   */
  showAlert(title, message, type = 'info') {
    const alertClass = `alert-${type}`;
    const iconClass = type === 'warning' ? 'fa-exclamation-triangle' : 
                     type === 'success' ? 'fa-check-circle' : 'fa-info-circle';
    
    const alertHtml = `
      <div class="alert ${alertClass} alert-dismissible fade show" role="alert">
        <i class="fas ${iconClass} me-2"></i>
        <strong>${title}:</strong> ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
      </div>
    `;
    
    // Inserir alerta no topo da seção de ações
    const actionsContainer = document.querySelector('.actions-section');
    if (actionsContainer) {
      actionsContainer.insertAdjacentHTML('afterbegin', alertHtml);
      
      // Auto-remover após 5 segundos
      setTimeout(() => {
        const alert = actionsContainer.querySelector('.alert');
        if (alert) {
          const bsAlert = new bootstrap.Alert(alert);
          bsAlert.close();
        }
      }, 5000);
    }
  }
  
  /**
   * Valida ação antes de executar
   */
  validateAction(action, callback) {
    const allowed = this.canPerformAction(action);
    
    if (!allowed) {
      this.showBusinessRuleInfo(`${action}_blocked`);
      return false;
    }
    
    if (typeof callback === 'function') {
      callback();
    }
    
    return true;
  }
  
  /**
   * Atualiza status dinamicamente (para updates via AJAX)
   */
  updateStatus(newStatus) {
    this.currentStatus = newStatus;
    document.body.className = document.body.className.replace(/status-\w+/, `status-${newStatus}`);
    this.validateCurrentState();
    this.setupEventListeners();
  }
}