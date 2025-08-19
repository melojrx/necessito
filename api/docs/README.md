# API Indicai v1.0

**Documentação Oficial da API RESTful do Sistema Indicai**

A API Indicai é uma interface RESTful moderna e robusta que permite integração completa com o ecossistema Indicai - a plataforma líder em conexão entre demandas e fornecedores de serviços.

---

## 📋 Índice

- [Visão Geral](#visão-geral)
- [Autenticação](#autenticação)
- [Versionamento](#versionamento)
- [Estrutura de Resposta](#estrutura-de-resposta)
- [Módulos da API](#módulos-da-api)
- [Permissões e Segurança](#permissões-e-segurança)
- [Rate Limiting](#rate-limiting)
- [Códigos de Status](#códigos-de-status)
- [Exemplos Práticos](#exemplos-práticos)
- [Arquitetura e Otimizações](#arquitetura-e-otimizações)
- [Suporte](#suporte)

---

## 🎯 Visão Geral

### Características Principais

- **RESTful**: Segue os princípios REST para máxima compatibilidade
- **Versionada**: Sistema de versionamento semântico para evolução controlada
- **Documentada**: Documentação interativa com Swagger/OpenAPI 3.0
- **Segura**: Autenticação JWT e sistema de permissões granular
- **Performática**: Paginação automática e filtros otimizados
- **Monitorada**: Logs detalhados e métricas de performance
- **Otimizada**: Arquitetura modular com classes base reutilizáveis

### URLs Base

```
Produção:    https://indicaai.com/api/v1/
Staging:     https://staging.indicaai.com/api/v1/
Desenvolvimento: http://localhost:8000/api/v1/
```

### Documentação Interativa

- **Swagger UI**: `/api/docs/` - Interface interativa para testar endpoints
- **ReDoc**: `/api/redoc/` - Documentação detalhada em formato limpo
- **Schema OpenAPI**: `/api/schema/` - Especificação OpenAPI 3.0 em JSON

---

## 🔐 Autenticação

A API Indicai utiliza autenticação JWT (JSON Web Tokens) com endpoint customizado otimizado para CORS.

### 🚀 Fluxo de Autenticação no Swagger

1. **Faça Login**: Use o endpoint `/api/v1/auth/login/` com seu email e senha
2. **Copie o Token**: Na resposta, copie o valor do campo `access`
3. **Clique em "Authorize"**: No topo da página do Swagger
4. **Cole o Token**: No campo "Value" (apenas o token, sem "Bearer")
5. **Autorize**: Clique em "Authorize" novamente
6. **Use a API**: Agora você pode usar todos os endpoints por 1 hora

### Métodos de Autenticação Disponíveis:

### 1. JWT (JSON Web Tokens) - Recomendado

Método principal para aplicações móveis e integrações de terceiros com endpoint customizado otimizado.

#### Obter Token

```http
POST /api/v1/auth/login/
Content-Type: application/json

{
    "email": "usuario@exemplo.com",
    "password": "senha_segura"
}
```

**Características do endpoint customizado:**
- ✅ Resolve problemas de CORS automaticamente
- ✅ Headers `Access-Control-Allow-Origin` configurados
- ✅ Suporte nativo a requisições OPTIONS (preflight)
- ✅ Validação robusta de credenciais
- ✅ Respostas de erro padronizadas

#### Resposta

```json
{
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "user": {
        "id": 123,
        "email": "usuario@exemplo.com",
        "first_name": "João",
        "last_name": "Silva",
        "tipo_usuario": "cliente"
    }
}
```

#### Usar Token

```http
GET /api/v1/necessidades/
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
```

#### Renovar Token

```http
POST /api/v1/auth/token/refresh/
Content-Type: application/json

{
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

#### Duração dos Tokens

- **Access Token**: 1 hora de validade
- **Refresh Token**: 7 dias de validade
- **Rotação**: Novo refresh token é gerado a cada renovação
- **Blacklist**: Refresh tokens anteriores são invalidados automaticamente

### 2. Registro de Usuários

```http
POST /api/v1/auth/registration/
Content-Type: application/json

{
    "email": "novo@exemplo.com",
    "password1": "senha_segura123",
    "password2": "senha_segura123",
    "first_name": "Maria",
    "last_name": "Santos",
    "tipo_usuario": "fornecedor"
}
```

---

## 📦 Versionamento

A API utiliza versionamento semântico via URL para garantir compatibilidade:

### Versão Atual: v1.0

- **URL**: `/api/v1/`
- **Status**: Estável
- **Suporte**: Até dezembro de 2026

### Informações de Versão

```http
GET /api/version/
```

```json
{
    "current_version": "1.0.0",
    "supported_versions": ["1.0"],
    "deprecated_versions": [],
    "api_info": {
        "title": "API Indicai",
        "description": "API RESTful para o sistema Indicai",
        "contact": "api@indicaai.com"
    }
}
```

---

## 📊 Estrutura de Resposta

### Resposta de Sucesso (Lista Paginada)

```json
{
    "count": 150,
    "next": "https://indicaai.com/api/v1/necessidades/?page=2",
    "previous": null,
    "results": [
        {
            "id": 1,
            "titulo": "Reforma de Banheiro",
            "descricao": "Necessito de reforma completa...",
            "created_at": "2025-01-10T14:30:00Z",
            "status": "ativo"
        }
    ]
}
```

### Resposta de Erro

```json
{
    "error": "Credenciais inválidas"
}
```

**ou para erros de validação:**

```json
{
    "email": ["Este campo é obrigatório."],
    "password": ["A senha deve ter pelo menos 8 caracteres."]
}
```

---

## 🏗️ Módulos da API

A API está organizada em 7 módulos principais com arquitetura otimizada:

### 00 - SISTEMA - INFORMAÇÕES GERAIS

Endpoints para informações do sistema e monitoramento.

- `GET /api/version/` - Informações de versão
- `GET /api/logout-redirect/` - Utilitário de logout

### 01 - USUÁRIOS - GESTÃO DE PERFIS

Gerenciamento completo de usuários (clientes e fornecedores).

```http
GET    /api/v1/users/           # Listar usuários
POST   /api/v1/users/           # Criar usuário
GET    /api/v1/users/{id}/      # Detalhes do usuário
PUT    /api/v1/users/{id}/      # Atualizar usuário
PATCH  /api/v1/users/{id}/      # Atualização parcial
DELETE /api/v1/users/{id}/      # Excluir usuário
```

**Campos principais:**
- `id`, `email`, `first_name`, `last_name`
- `is_client`, `is_supplier`, `cidade`, `estado`
- `telefone`, `endereco`, `foto_perfil`
- `is_active`, `email_verificado`

**Filtros disponíveis:**
- `is_client`, `is_supplier` - Filtrar por tipo de usuário
- `cidade`, `estado` - Filtrar por localização
- `search` - Busca em nome e email

### 02 - CATEGORIAS - CLASSIFICAÇÃO DE SERVIÇOS

Gestão das categorias principais de serviços.

```http
GET    /api/v1/categorias/           # Listar categorias
POST   /api/v1/categorias/           # Criar categoria (Admin)
GET    /api/v1/categorias/{id}/      # Detalhes da categoria
PUT    /api/v1/categorias/{id}/      # Atualizar categoria (Admin)
PATCH  /api/v1/categorias/{id}/      # Atualização parcial (Admin)
DELETE /api/v1/categorias/{id}/      # Excluir categoria (Admin)
```

**Campos principais:**
- `id`, `nome`, `descricao`
- `icone`, `imagem_local`, `url_imagem_externa`
- `ativa`, `ordem`

**Permissões:** IsAuthenticatedOrReadOnly + IsAdminOrReadOnly

### 03 - SUBCATEGORIAS - ESPECIALIZAÇÃO DE SERVIÇOS

Gestão das subcategorias para especialização de serviços.

```http
GET    /api/v1/subcategorias/           # Listar subcategorias
POST   /api/v1/subcategorias/           # Criar subcategoria (Admin)
GET    /api/v1/subcategorias/{id}/      # Detalhes da subcategoria
PUT    /api/v1/subcategorias/{id}/      # Atualizar subcategoria (Admin)
PATCH  /api/v1/subcategorias/{id}/      # Atualização parcial (Admin)
DELETE /api/v1/subcategorias/{id}/      # Excluir subcategoria (Admin)
```

**Filtros disponíveis:**
- `categoria` - Filtrar por categoria pai
- `search` - Busca em nome e descrição

### 04 - NECESSIDADES - ANÚNCIOS DE DEMANDA

Gerenciamento de anúncios de necessidades dos clientes.

```http
GET    /api/v1/necessidades/           # Listar necessidades
POST   /api/v1/necessidades/           # Criar necessidade
GET    /api/v1/necessidades/{id}/      # Detalhes da necessidade
PUT    /api/v1/necessidades/{id}/      # Atualizar necessidade
PATCH  /api/v1/necessidades/{id}/      # Atualização parcial
DELETE /api/v1/necessidades/{id}/      # Excluir necessidade
```

**Campos principais:**
- `id`, `titulo`, `descricao`
- `cliente` (atribuído automaticamente ao criar)
- `categoria`, `subcategoria`
- `quantidade`, `unidade`, `valor_estimado`
- `prazo_execucao`, `endereco_execucao`
- `status` (ativo/pausado/finalizado)

**Filtros automáticos:**
- Usuários não-staff só veem necessidades com `status='ativo'`
- Cliente sempre atribuído automaticamente na criação

**Serializers diferenciados:**
- Lista: `NecessidadeSerializer` (campos básicos)
- Detalhes: `NecessidadeDetailSerializer` (informações completas)

### 05 - ORÇAMENTOS - PROPOSTAS DE FORNECEDORES

Gestão de orçamentos/propostas dos fornecedores.

```http
GET    /api/v1/orcamentos/           # Listar orçamentos
POST   /api/v1/orcamentos/           # Criar orçamento
GET    /api/v1/orcamentos/{id}/      # Detalhes do orçamento
PUT    /api/v1/orcamentos/{id}/      # Atualizar orçamento
PATCH  /api/v1/orcamentos/{id}/      # Atualização parcial
DELETE /api/v1/orcamentos/{id}/      # Excluir orçamento
```

**Campos principais:**
- `id`, `necessidade`, `fornecedor` (atribuído automaticamente)
- `valor`, `descricao`, `prazo_execucao`
- `status` (enviado/aceito/rejeitado/finalizado)
- `anexos`, `observacoes`

**Filtros de segurança:**
- Usuários só veem orçamentos onde são fornecedores OU clientes da necessidade
- Query otimizada: `Q(fornecedor=user) | Q(anuncio__cliente=user)`

### 06 - AVALIAÇÕES - SISTEMA DE REPUTAÇÃO

Sistema de avaliações entre clientes e fornecedores.

```http
GET    /api/v1/avaliacoes/           # Listar avaliações
POST   /api/v1/avaliacoes/           # Criar avaliação
GET    /api/v1/avaliacoes/{id}/      # Detalhes da avaliação
PUT    /api/v1/avaliacoes/{id}/      # Atualizar avaliação
PATCH  /api/v1/avaliacoes/{id}/      # Atualização parcial
DELETE /api/v1/avaliacoes/{id}/      # Excluir avaliação
```

**Campos principais:**
- `id`, `usuario` (avaliador - atribuído automaticamente), `avaliado`, `orcamento`
- `nota` (1-5), `comentario`
- `tipo_avaliacao` (cliente_para_fornecedor/fornecedor_para_cliente)

### 07 - AUTENTICAÇÃO - ACESSO AO SISTEMA

Endpoints para autenticação e gestão de sessões.

```http
POST   /api/v1/auth/login/              # Login customizado (CORS otimizado)
POST   /api/v1/auth/logout/             # Logout
POST   /api/v1/auth/registration/       # Registro
POST   /api/v1/auth/password/change/    # Alterar senha
POST   /api/v1/auth/password/reset/     # Solicitar reset de senha
POST   /api/v1/auth/token/refresh/      # Renovar token JWT
GET    /api/v1/auth/user/               # Dados do usuário atual
```

---

## 🔒 Permissões e Segurança

### Sistema de Permissões Customizadas

A API implementa permissões específicas para cada recurso:

#### 1. Permissões por Recurso
- **NecessidadePermission**: Controle específico para necessidades
- **OrcamentoPermission**: Controle específico para orçamentos  
- **AvaliacaoPermission**: Controle específico para avaliações
- **IsAdminOrReadOnly**: Apenas admins podem modificar recursos do sistema

#### 2. Filtros Automáticos de Segurança (BaseModelViewSet)

Implementados na classe base para todos os ViewSets:

```python
class BaseModelViewSet(viewsets.ModelViewSet):
    """ViewSet base com configurações comuns e filtros de segurança automáticos"""
    
    def get_queryset(self):
        # Filtragem automática para usuários não-staff
        if not self.request.user.is_staff:
            return self._filter_for_regular_user(queryset)
        return queryset
```

**Filtros específicos por modelo:**
- **Usuários**: `is_active=True` (só usuários ativos)
- **Necessidades**: `status='ativo'` (só necessidades ativas)
- **Orçamentos**: `Q(fornecedor=user) | Q(anuncio__cliente=user)` (só relacionados)
- **Avaliações**: Sem filtro adicional (visíveis publicamente)

#### 3. Atribuição Automática de Propriedade

```python
def perform_create(self, serializer):
    # Atribuição automática do usuário atual
    serializer.save(usuario_field=self.request.user)
```

- **Necessidades**: `cliente` atribuído automaticamente
- **Orçamentos**: `fornecedor` atribuído automaticamente  
- **Avaliações**: `usuario` (avaliador) atribuído automaticamente

### Validações de Segurança

- ✅ Validação de propriedade em todas as operações
- ✅ Filtros automáticos por tipo de usuário
- ✅ Sanitização de dados de entrada
- ✅ Logs de auditoria para operações sensíveis

---

## ⚡ Performance e Otimizações

### Arquitetura Modular Otimizada

#### 1. BaseModelViewSet - Classe Base Reutilizável

Todos os ViewSets herdam da `BaseModelViewSet` que fornece:

```python
class BaseModelViewSet(viewsets.ModelViewSet):
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    
    def get_queryset(self):
        """Filtragem automática para usuários não-staff"""
        queryset = super().get_queryset()
        if not self.request.user.is_staff:
            queryset = self._filter_for_regular_user(queryset)
        return queryset
```

**Benefícios:**
- ✅ Eliminação de código duplicado
- ✅ Configuração consistente de filtros
- ✅ Lógica de segurança centralizada
- ✅ Manutenção simplificada

#### 2. Estrutura de Arquivos Otimizada

```
api/
├── views.py          # ViewSets principais (6 classes, ~190 linhas)
├── auth_views.py     # Autenticação customizada (~120 linhas)
├── v1/
│   └── address_views.py  # Views específicas de endereço
├── serializers.py    # Serializers organizados
├── permissions.py    # Permissões customizadas
├── filters.py        # Filtros específicos
└── docs/
    └── README.md     # Documentação (este arquivo)
```

**Otimizações implementadas:**
- 🗑️ Removido `views_old.py` (930 linhas de código legado)
- 📁 Renomeado `views_clean.py` → `auth_views.py` (melhor nomenclatura)
- 🔄 Refatorado todos ViewSets para usar `BaseModelViewSet`
- 📚 Documentação atualizada e reorganizada

#### 3. Filtros e Buscas Otimizados

- **DjangoFilterBackend**: Filtros eficientes via query parameters
- **SearchFilter**: Busca otimizada em campos específicos
- **Paginação automática**: Performance melhorada em listas grandes
- **Queryset filtering**: Redução de dados desnecessários

### Performance Features

- **Serializers diferenciados**: Lista vs. Detail para reduzir payload
- **Filtros automáticos**: Redução de queries desnecessárias  
- **Lazy loading**: Carregamento otimizado de relacionamentos
- **Query optimization**: Filtros aplicados no banco de dados

---

## 📋 Códigos de Status

### Códigos de Sucesso

- `200 OK` - Requisição bem-sucedida
- `201 Created` - Recurso criado com sucesso
- `204 No Content` - Operação bem-sucedida sem conteúdo de retorno

### Códigos de Erro do Cliente

- `400 Bad Request` - Dados inválidos
- `401 Unauthorized` - Não autenticado
- `403 Forbidden` - Sem permissão
- `404 Not Found` - Recurso não encontrado
- `409 Conflict` - Conflito de dados
- `422 Unprocessable Entity` - Erro de validação

### Códigos de Erro do Servidor

- `500 Internal Server Error` - Erro interno do servidor
- `502 Bad Gateway` - Erro de gateway
- `503 Service Unavailable` - Serviço indisponível

---

## 💡 Exemplos Práticos

### 1. Fluxo Completo: Cliente Criando Necessidade

```javascript
// 1. Autenticação com endpoint customizado
const loginResponse = await fetch('/api/v1/auth/login/', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
    },
    body: JSON.stringify({
        email: 'cliente@exemplo.com',
        password: 'senha123'
    })
});

const { access } = await loginResponse.json();

// 2. Listar categorias (sem autenticação necessária)
const categoriasResponse = await fetch('/api/v1/categorias/');
const categorias = await categoriasResponse.json();

// 3. Criar necessidade (cliente atribuído automaticamente)
const necessidadeResponse = await fetch('/api/v1/necessidades/', {
    method: 'POST',
    headers: {
        'Authorization': `Bearer ${access}`,
        'Content-Type': 'application/json',
    },
    body: JSON.stringify({
        titulo: 'Reforma de Cozinha',
        descricao: 'Preciso reformar minha cozinha completamente...',
        categoria: 1,
        subcategoria: 5,
        quantidade: 1,
        unidade: 'un',
        valor_estimado: 15000.00,
        prazo_execucao: '2025-02-15'
        // cliente é atribuído automaticamente
    })
});

const necessidade = await necessidadeResponse.json();
```

### 2. Fornecedor Enviando Orçamento

```python
import requests

# Autenticação
auth_response = requests.post('http://localhost:8000/api/v1/auth/login/', json={
    'email': 'fornecedor@exemplo.com',
    'password': 'senha123'
})

token = auth_response.json()['access']
headers = {'Authorization': f'Bearer {token}'}

# Buscar necessidades ativas (filtradas automaticamente)
necessidades = requests.get(
    'http://localhost:8000/api/v1/necessidades/',
    headers=headers
).json()

# Enviar orçamento (fornecedor atribuído automaticamente)
orcamento_data = {
    'necessidade': 123,
    'valor': 12500.00,
    'descricao': 'Proposta para reforma completa da cozinha...',
    'prazo_execucao': '2025-02-10',
    'observacoes': 'Inclui material e mão de obra'
    # fornecedor é atribuído automaticamente
}

orcamento_response = requests.post(
    'http://localhost:8000/api/v1/orcamentos/',
    json=orcamento_data,
    headers=headers
)
```

### 3. Sistema de Avaliações

```javascript
// Após conclusão do serviço, cliente avalia fornecedor
const avaliacaoData = {
    avaliado: 456, // ID do fornecedor
    orcamento: 789, // ID do orçamento
    nota: 5,
    comentario: 'Excelente trabalho! Muito profissional e pontual.',
    tipo_avaliacao: 'cliente_para_fornecedor'
    // usuario (avaliador) é atribuído automaticamente
};

const avaliacaoResponse = await fetch('/api/v1/avaliacoes/', {
    method: 'POST',
    headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
    },
    body: JSON.stringify(avaliacaoData)
});
```

---

## 📞 Suporte

### Canais de Suporte

- **Email**: api@indicaai.com
- **Discord**: [Comunidade Indicai Developers](https://discord.gg/indicaai)
- **GitHub**: [Issues e Discussões](https://github.com/indicaai/api-issues)
- **Documentação**: [docs.indicaai.com](https://docs.indicaai.com)

### SLA (Service Level Agreement)

- **Uptime**: 99.9%
- **Tempo de resposta**: < 200ms (P95)
- **Suporte**: 24/7 para clientes enterprise

### Status da API

Monitore o status em tempo real: [status.indicaai.com](https://status.indicaai.com)

---

## 📄 Changelog

### v1.0.1 (2025-01-19)

- 🔧 **Otimização da arquitetura**: Criação da `BaseModelViewSet` para reduzir duplicação de código
- 🗑️ **Limpeza de código**: Removido arquivo legado `views_old.py` (930 linhas)
- 📁 **Reorganização**: Renomeado `views_clean.py` → `auth_views.py` para melhor nomenclatura
- ⚡ **Performance**: Filtros automáticos de segurança otimizados
- 🔒 **Segurança**: Atribuição automática de propriedade em todos os recursos
- 📚 **Documentação**: Atualização completa da documentação com exemplos práticos

### v1.0.0 (2025-01-10)

- 🎉 Lançamento inicial da API
- ✅ Autenticação JWT implementada
- ✅ Sistema de permissões granular
- ✅ Documentação Swagger completa
- ✅ 7 módulos principais disponíveis

---

**© 2025 Indicai. Todos os direitos reservados.**

*Esta documentação é mantida pela equipe de desenvolvimento da Indicai e é atualizada regularmente. Para sugestões ou correções, entre em contato através dos canais oficiais.*