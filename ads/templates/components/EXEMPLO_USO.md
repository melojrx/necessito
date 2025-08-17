# Como Usar os Componentes de Status

## Estrutura dos Componentes

Cada componente foi criado para ser completamente independente e responsivo às regras de negócio específicas de cada status.

### Inclusão no Template Principal

```html
<!-- No necessidade_detail.html -->
<div class="actions-section mb-4">
  {% if necessidade.status == 'ativo' %}
    {% include 'components/actions/status_ativo.html' %}
  {% elif necessidade.status == 'analisando_orcamentos' %}
    {% include 'components/actions/status_analisando.html' %}
  {% elif necessidade.status == 'aguardando_confirmacao' %}
    {% include 'components/actions/status_aguardando.html' %}
  {% elif necessidade.status == 'em_atendimento' %}
    {% include 'components/actions/status_em_atendimento.html' %}
  {% elif necessidade.status == 'finalizado' %}
    {% include 'components/actions/status_finalizado.html' %}
  {% endif %}
</div>
```

## Variáveis de Contexto Necessárias

Cada componente espera as seguintes variáveis no contexto do template:

```python
# View context
context = {
    'necessidade': necessidade_instance,
    'user': request.user,
    'avaliacao_cliente': avaliacao_do_cliente,  # se existe
    'avaliacao_fornecedor': avaliacao_do_fornecedor,  # se existe
    'usuario_tem_orcamento': boolean,  # se o fornecedor atual já enviou orçamento
}
```

## Integração com JavaScript

### Inicialização do StatusValidator

```javascript
document.addEventListener('DOMContentLoaded', function() {
  const statusValidator = new StatusValidator(
    necessidadeId,
    currentStatus,
    userType,     // 'cliente', 'fornecedor', 'visitante'
    userId,
    clienteId
  );
});
```

### Uso das Validações

```javascript
// Verificar se pode editar
if (statusValidator.canEdit()) {
  // Habilitar botão de edição
}

// Validar ação antes de executar
statusValidator.validateAction('enviar_orcamento', () => {
  // Callback executado se a ação for válida
});
```

## Personalização dos Componentes

### Adicionando Novos Status

Para adicionar um novo status, siga estes passos:

1. **Crie o componente HTML**:
   ```bash
   touch ads/templates/components/actions/status_meu_novo_status.html
   ```

2. **Inclua no template principal**:
   ```html
   {% elif necessidade.status == 'meu_novo_status' %}
     {% include 'components/actions/status_meu_novo_status.html' %}
   ```

3. **Adicione as regras no JavaScript**:
   ```javascript
   statusRules: {
     'meu_novo_status': {
       cliente: ['acao1', 'acao2'],
       fornecedor: ['acao3'],
       visitante: []
     }
   }
   ```

### Estrutura Recomendada do Componente

```html
<!-- status_exemplo.html -->
<div class="status-actions-container" data-status="exemplo">
  <div class="row g-3">
    
    <!-- Card para cliente -->
    {% if user.is_authenticated and user == necessidade.cliente %}
    <div class="col-12">
      <div class="card border-primary shadow-sm">
        <div class="card-header bg-primary text-white">
          <h6 class="mb-0">
            <i class="fas fa-icon me-2"></i>
            Título da Seção
          </h6>
        </div>
        <div class="card-body">
          <!-- Conteúdo específico para o cliente -->
        </div>
      </div>
    </div>
    {% endif %}

    <!-- Card para fornecedores -->
    {% if user.is_authenticated and user != necessidade.cliente %}
    <!-- Conteúdo para fornecedores -->
    {% endif %}

    <!-- Card para visitantes -->
    {% if not user.is_authenticated %}
    <!-- Conteúdo para não logados -->
    {% endif %}

    <!-- Card de informações do status -->
    <div class="col-12">
      <div class="card bg-light border-0">
        <div class="card-body py-2">
          <div class="d-flex align-items-center">
            <div class="status-indicator bg-primary me-2"></div>
            <small class="text-muted">
              <strong>Status:</strong> Descrição do status atual
            </small>
          </div>
        </div>
      </div>
    </div>
  </div>
</div>
```

## Boas Práticas

### 1. **Atributos data-action**
Sempre adicione `data-action` aos botões para integração com o StatusValidator:

```html
<button class="btn btn-primary" data-action="minha-acao">
  Minha Ação
</button>
```

### 2. **Feedback Visual**
Use as classes CSS predefinidas para consistência:

```html
<!-- Sucesso -->
<div class="alert alert-success">
  <i class="fas fa-check-circle me-1"></i>
  Mensagem de sucesso
</div>

<!-- Aviso -->
<div class="alert alert-warning">
  <i class="fas fa-exclamation-triangle me-1"></i>
  Mensagem de aviso
</div>
```

### 3. **Responsividade**
Use o sistema de grid do Bootstrap:

```html
<div class="row g-3">
  <div class="col-12 col-md-6">
    <!-- Conteúdo que ocupa metade em desktop -->
  </div>
  <div class="col-12 col-md-6">
    <!-- Outra metade -->
  </div>
</div>
```

### 4. **Acessibilidade**
Sempre inclua atributos ARIA e títulos descritivos:

```html
<button class="btn btn-primary" 
        title="Descrição da ação"
        aria-label="Texto para screen readers">
  <i class="fas fa-icon" aria-hidden="true"></i>
  Texto do Botão
</button>
```

## Testando as Implementações

### 1. **Teste Manual**
- Acesse a página com diferentes tipos de usuário
- Verifique se os componentes corretos aparecem para cada status
- Teste as ações disponíveis

### 2. **Teste de Validações**
```javascript
// No console do navegador
console.log(statusValidator.canEdit()); // true/false
console.log(statusValidator.canPerformAction('enviar_orcamento')); // true/false
```

### 3. **Teste de Responsividade**
- Redimensione a janela do navegador
- Verifique se os cards se reorganizam corretamente
- Teste em dispositivos móveis

## Solução de Problemas Comuns

### Componente não aparece
- Verifique se o status está correto na condição `{% if %}`
- Confirme que o arquivo do componente existe
- Verifique se não há erros de sintaxe no template

### JavaScript não funciona
- Verifique se o `status_validator.js` está sendo carregado
- Confirme que as variáveis estão sendo passadas corretamente
- Abra o console do navegador para ver erros

### Estilos não aplicados
- Verifique se o CSS customizado está na seção `<style>` do template
- Confirme que não há conflitos com outros estilos
- Use ferramentas de desenvolvedor para debugar CSS

## Monitoramento e Métricas

Para acompanhar a efetividade das melhorias:

```javascript
// Adicionar tracking de eventos
document.querySelectorAll('[data-action]').forEach(btn => {
  btn.addEventListener('click', function() {
    // Analytics tracking
    gtag('event', 'click', {
      'event_category': 'necessidade_detail',
      'event_label': this.dataset.action,
      'status': currentStatus
    });
  });
});
```