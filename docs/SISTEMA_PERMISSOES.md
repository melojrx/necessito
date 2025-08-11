# Sistema de Permissões e Autenticação - Indicai

## Visão Geral

O sistema de permissões do Indicai é baseado em **papéis de usuário** e **verificações de propriedade**, garantindo que cada usuário tenha acesso apenas às funcionalidades e recursos apropriados para seu perfil.

## Papéis de Usuário

### 1. **Administrador da Plataforma**
- **Campo**: `user.is_staff = True`
- **Permissões**: Acesso total ao sistema, incluindo dashboard administrativo
- **Funcionalidades**: Gerenciamento de usuários, métricas, configurações

### 2. **Cliente/Anunciante**
- **Campo**: `user.is_client = True`
- **Permissões**: Criar anúncios, aceitar/rejeitar orçamentos, finalizar negócios
- **Funcionalidades**: Postar necessidades, gerenciar anúncios, avaliar fornecedores

### 3. **Fornecedor**
- **Campo**: `user.is_supplier = True`
- **Permissões**: Criar orçamentos, responder a anúncios
- **Funcionalidades**: Submeter propostas, gerenciar orçamentos, avaliar clientes

**Nota**: Um usuário pode ter múltiplos papéis (ser cliente E fornecedor simultaneamente).

## Verificações de Segurança

### 1. **Verificação de E-mail**
- **Campo**: `user.email_verified = True`
- **Obrigatório para**: Criar anúncios, criar orçamentos
- **Processo**: Token enviado por e-mail com validade de 24 horas

### 2. **Perfil Completo**
- **Critério**: `user.is_client = True` OU `user.is_supplier = True`
- **Middleware**: Sugere completar perfil após login (não bloqueia)

## Ferramentas de Controle de Acesso

### 1. **Decorators para Function-Based Views**

```python
from core.decorators import client_required, supplier_required, admin_required

@client_required
def criar_anuncio(request):
    # Apenas clientes podem acessar
    pass

@supplier_required
def criar_orcamento(request):
    # Apenas fornecedores podem acessar
    pass

@admin_required
def dashboard(request):
    # Apenas administradores podem acessar
    pass
```

### 2. **Mixins para Class-Based Views**

```python
from core.mixins import ClientRequiredMixin, SupplierRequiredMixin

class CriarAnuncioView(ClientRequiredMixin, CreateView):
    # Apenas clientes podem criar anúncios
    pass

class CriarOrcamentoView(SupplierRequiredMixin, CreateView):
    # Apenas fornecedores podem criar orçamentos
    pass
```

### 3. **Validador de Permissões Centralizado**

```python
from core.permissions import PermissionValidator

# Verificar se pode criar anúncio
can_create, message = PermissionValidator.can_create_ad(request.user)
if not can_create:
    messages.error(request, message)
    return redirect('home')
```

## Regras de Negócio por Funcionalidade

### **Anúncios/Necessidades**

| Ação | Permissão Necessária | Regras Adicionais |
|------|---------------------|-------------------|
| Criar | Cliente + E-mail verificado | - |
| Editar | Proprietário | Status não pode ser 'finalizado' ou 'cancelado' |
| Visualizar | Todos | - |
| Finalizar | Proprietário | Deve ter orçamento aceito |
| Deletar | Proprietário | Status deve permitir exclusão |

### **Orçamentos**

| Ação | Permissão Necessária | Regras Adicionais |
|------|---------------------|-------------------|
| Criar | Fornecedor + E-mail verificado | Anúncio deve estar ativo |
| Editar | Proprietário | Status não pode ser 'aceito' ou 'rejeitado' |
| Visualizar | Proprietário OU Cliente do anúncio | - |
| Aceitar | Cliente do anúncio | Status deve ser 'pendente' |
| Rejeitar | Cliente do anúncio | Status deve ser 'pendente' |
| Deletar | Proprietário | Status não pode ser 'aguardando' |

### **Avaliações**

| Ação | Permissão Necessária | Regras Adicionais |
|------|---------------------|-------------------|
| Criar | Cliente OU Fornecedor | Anúncio deve estar 'finalizado' |
| Visualizar | Todos | - |
| Editar | Proprietário | Dentro do prazo permitido |

## Implementação nas Views

### **Exemplo: View de Criar Anúncio**

```python
from core.mixins import ClientRequiredMixin, EmailVerifiedRequiredMixin
from core.permissions import PermissionValidator

class NecessidadeCreateView(ClientRequiredMixin, EmailVerifiedRequiredMixin, CreateView):
    model = Necessidade
    form_class = AdsForms
    
    def form_valid(self, form):
        # Validação adicional
        can_create, message = PermissionValidator.can_create_ad(self.request.user)
        if not can_create:
            messages.error(self.request, message)
            return redirect('home')
        
        # Continuar com a criação
        self.object = form.save(commit=False)
        self.object.cliente = self.request.user
        self.object.save()
        return super().form_valid(form)
```

### **Exemplo: View de Aceitar Orçamento**

```python
from core.permissions import PermissionValidator

class OrcamentoAceitarView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        orcamento = get_object_or_404(Orcamento, id=kwargs['pk'])
        
        # Verificar permissão
        can_accept, message = PermissionValidator.can_accept_budget(request.user, orcamento)
        if not can_accept:
            return JsonResponse({'error': message}, status=403)
        
        # Processar aceitação
        orcamento.status = 'aguardando'
        orcamento.save()
        
        return JsonResponse({'success': True})
```

## Middleware de Perfil Completo

O `ProfileCompleteMiddleware` funciona de forma **não-intrusiva**:

1. **Sugere** completar perfil apenas uma vez por sessão
2. **Não bloqueia** o acesso às funcionalidades
3. **Permite pular** a sugestão
4. **Funciona apenas** em páginas principais

### Configuração

```python
# settings/base.py
MIDDLEWARE = [
    # ... outros middlewares
    "core.middleware.ProfileCompleteMiddleware",
]
```

## Tratamento de Erros

### **403 - Acesso Negado**
- Template: `templates/403.html`
- Usado quando usuário não tem permissão

### **Redirecionamentos**
- **Login**: Usuário não autenticado
- **Complete Profile**: Usuário sem papel definido
- **Email Verification**: E-mail não verificado

## Segurança Adicional

### **Verificações de Propriedade**
Todas as views que manipulam recursos verificam se o usuário é o proprietário:

```python
# Verificar se é dono do anúncio
if request.user != anuncio.cliente:
    raise PermissionDenied("Você não tem permissão para editar este anúncio.")

# Verificar se é dono do orçamento
if request.user != orcamento.fornecedor:
    raise PermissionDenied("Você não tem permissão para editar este orçamento.")
```

### **Validação de Status**
Operações são validadas com base no status do objeto:

```python
# Não permitir edição de anúncios finalizados
if anuncio.status in ['finalizado', 'cancelado']:
    raise PermissionDenied("Não é possível editar anúncios finalizados.")
```

## API REST

### **Permissões da API**

```python
# api/permissions.py
class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.cliente == request.user or obj.fornecedor == request.user
```

### **Configuração REST Framework**

```python
# settings/base.py
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}
```

## Boas Práticas

1. **Sempre validar permissões** antes de processar ações
2. **Usar mensagens claras** para orientar o usuário
3. **Redirecionar adequadamente** para páginas de correção
4. **Logar tentativas** de acesso não autorizado
5. **Testar todas as combinações** de papéis e estados

## Troubleshooting

### **Usuário não consegue criar anúncio**
1. Verificar se `is_client = True`
2. Verificar se `email_verified = True`
3. Verificar se está logado

### **Middleware redirecionando constantemente**
1. Verificar se `profile_completion_suggested` está na sessão
2. Verificar URLs exemtas
3. Verificar se é requisição AJAX

### **403 Forbidden inesperado**
1. Verificar propriedade do objeto
2. Verificar status do objeto
3. Verificar papel do usuário

## Testes

```python
# tests/test_permissions.py
from django.test import TestCase
from core.permissions import PermissionValidator

class PermissionTests(TestCase):
    def test_client_can_create_ad(self):
        user = User.objects.create_user(
            email='test@test.com',
            is_client=True,
            email_verified=True
        )
        can_create, message = PermissionValidator.can_create_ad(user)
        self.assertTrue(can_create)
    
    def test_supplier_cannot_create_ad(self):
        user = User.objects.create_user(
            email='test@test.com',
            is_supplier=True,
            email_verified=True
        )
        can_create, message = PermissionValidator.can_create_ad(user)
        self.assertFalse(can_create)
```

---

Este sistema de permissões garante que o Indicai seja seguro, intuitivo e que cada usuário tenha acesso apenas às funcionalidades apropriadas para seu perfil. 