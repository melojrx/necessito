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
- [SDKs e Bibliotecas](#sdks-e-bibliotecas)
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

### URLs Base

```
Produção:    https://indicaai.com/api/v1/
Staging:     https://staging.indicaai.com/api/v1/
Desenvolvimento: http://localhost:8000/api/v1/
```

### Documentação Interativa

- **Swagger UI**: `/api/swagger/` - Interface interativa para testar endpoints
- **ReDoc**: `/api/redoc/` - Documentação detalhada em formato limpo
- **Schema OpenAPI**: `/api/schema/` - Especificação OpenAPI 3.0 em JSON

---

## 🔐 Autenticação

A API Indicai utiliza autenticação JWT (JSON Web Tokens). Siga o fluxo abaixo para autenticar-se no Swagger:

### 🚀 Fluxo de Autenticação no Swagger

1. **Faça Login**: Use o endpoint `/api/v1/auth/login/` com seu email e senha
2. **Copie o Token**: Na resposta, copie o valor do campo `access`
3. **Clique em "Authorize"**: No topo da página do Swagger
4. **Cole o Token**: No campo "Value" (apenas o token, sem "Bearer")
5. **Autorize**: Clique em "Authorize" novamente
6. **Use a API**: Agora você pode usar todos os endpoints por 1 hora

### Métodos de Autenticação Disponíveis:

### 1. JWT (JSON Web Tokens) - Recomendado

Método principal para aplicações móveis e integrações de terceiros.

#### Obter Token

```http
POST /api/v1/auth/login/
Content-Type: application/json

{
    "email": "usuario@exemplo.com",
    "password": "senha_segura"
}
```

**Nota importante**: O endpoint usa apenas `email` e `password`. Não é necessário fornecer `username`.

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

**Recomendação**: Implemente renovação automática do access token quando ele estiver próximo do vencimento.

### 2. Autenticação de Sessão

Para uso no navegador web (interface administrativa).

```http
POST /api/v1/auth/login/
Content-Type: application/json
X-CSRFToken: [csrf-token]

{
    "email": "usuario@exemplo.com",
    "password": "senha_segura"
}
```

**Nota**: Mesmo endpoint, mesmos campos. A diferença é que a autenticação de sessão também cria um cookie de sessão além do JWT.

### 3. Registro de Usuários

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

### Resposta de Sucesso

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
    "error": {
        "code": "VALIDATION_ERROR",
        "message": "Dados inválidos fornecidos",
        "details": {
            "email": ["Este campo é obrigatório."],
            "password": ["A senha deve ter pelo menos 8 caracteres."]
        },
        "timestamp": "2025-01-10T14:30:00Z",
        "request_id": "req_123456789"
    }
}
```

---

## 🏗️ Módulos da API

A API está organizada em 8 módulos principais:

### 00 - SISTEMA - INFORMAÇÕES GERAIS

Endpoints para informações do sistema e monitoramento.

- `GET /api/version/` - Informações de versão
- `GET /api/health/` - Status de saúde do sistema
- `GET /api/stats/` - Estatísticas gerais

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
- `tipo_usuario` (cliente/fornecedor)
- `telefone`, `endereco`, `cidade`, `estado`
- `foto_perfil`, `descricao_perfil`
- `email_verificado`, `ativo`

### 02 - CATEGORIAS - CLASSIFICAÇÃO DE SERVIÇOS

Gestão das categorias principais de serviços.

```http
GET    /api/v1/categorias/           # Listar categorias
POST   /api/v1/categorias/           # Criar categoria
GET    /api/v1/categorias/{id}/      # Detalhes da categoria
PUT    /api/v1/categorias/{id}/      # Atualizar categoria
PATCH  /api/v1/categorias/{id}/      # Atualização parcial
DELETE /api/v1/categorias/{id}/      # Excluir categoria
```

**Campos principais:**
- `id`, `nome`, `descricao`
- `icone`, `imagem_local`, `url_imagem_externa`
- `ativa`, `ordem`

### 03 - SUBCATEGORIAS - ESPECIALIZAÇÃO DE SERVIÇOS

Gestão das subcategorias para especialização de serviços.

```http
GET    /api/v1/subcategorias/           # Listar subcategorias
POST   /api/v1/subcategorias/           # Criar subcategoria
GET    /api/v1/subcategorias/{id}/      # Detalhes da subcategoria
PUT    /api/v1/subcategorias/{id}/      # Atualizar subcategoria
PATCH  /api/v1/subcategorias/{id}/      # Atualização parcial
DELETE /api/v1/subcategorias/{id}/      # Excluir subcategoria
```

**Filtros disponíveis:**
- `categoria` - Filtrar por categoria pai
- `ativa` - Apenas subcategorias ativas

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
- `cliente`, `categoria`, `subcategoria`
- `quantidade`, `unidade`, `valor_estimado`
- `prazo_execucao`, `endereco_execucao`
- `status` (ativo/pausado/finalizado)
- `imagens`, `created_at`, `updated_at`

**Filtros e busca:**
- `status` - Filtrar por status
- `categoria` - Filtrar por categoria
- `subcategoria` - Filtrar por subcategoria
- `cliente` - Filtrar por cliente
- `search` - Busca em título e descrição

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
- `id`, `necessidade`, `fornecedor`
- `valor`, `descricao`, `prazo_execucao`
- `status` (enviado/aceito/rejeitado/finalizado)
- `anexos`, `observacoes`
- `created_at`, `updated_at`

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
- `id`, `avaliador`, `avaliado`, `orcamento`
- `nota` (1-5), `comentario`
- `tipo_avaliacao` (cliente_para_fornecedor/fornecedor_para_cliente)
- `created_at`

### 07 - AUTENTICAÇÃO - ACESSO AO SISTEMA

Endpoints para autenticação e gestão de sessões.

```http
POST   /api/v1/auth/login/              # Login
POST   /api/v1/auth/logout/             # Logout
POST   /api/v1/auth/registration/       # Registro
POST   /api/v1/auth/password/change/    # Alterar senha
POST   /api/v1/auth/password/reset/     # Solicitar reset de senha
POST   /api/v1/auth/token/refresh/      # Renovar token JWT
GET    /api/v1/auth/user/               # Dados do usuário atual
```

---

## 🔒 Permissões e Segurança

### Sistema de Permissões

A API implementa um sistema granular de permissões:

#### 1. Permissões de Propriedade
- **IsOwnerOrReadOnly**: Usuários só podem editar seus próprios recursos
- **IsOwnerOrRelatedUser**: Acesso restrito a proprietários ou usuários relacionados

#### 2. Permissões de Tipo de Usuário
- **ClientePermission**: Restrições específicas para clientes
- **FornecedorPermission**: Restrições específicas para fornecedores

#### 3. Permissões de Admin
- **IsAdminOrReadOnly**: Apenas administradores podem modificar recursos do sistema

### Filtros Automáticos de Segurança

- **Usuários**: Só veem seus próprios dados
- **Necessidades**: Clientes veem suas necessidades, fornecedores veem necessidades públicas
- **Orçamentos**: Acesso restrito ao fornecedor e cliente relacionados
- **Avaliações**: Visíveis publicamente, mas criação restrita aos envolvidos

### Validações de Segurança

- Validação de propriedade em todas as operações de escrita
- Sanitização automática de dados de entrada
- Rate limiting por usuário e IP
- Logs de auditoria para operações sensíveis

---

## ⚡ Rate Limiting

Para garantir a qualidade do serviço, a API implementa rate limiting:

### Limites por Tipo de Usuário

- **Usuários autenticados**: 1000 requests/hora
- **Usuários não autenticados**: 100 requests/hora
- **Usuários premium**: 5000 requests/hora

### Headers de Rate Limit

```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1641024000
```

### Resposta de Rate Limit Excedido

```json
{
    "error": {
        "code": "RATE_LIMIT_EXCEEDED",
        "message": "Taxa de requisições excedida",
        "details": {
            "limit": 1000,
            "reset_time": "2025-01-10T15:00:00Z"
        }
    }
}
```

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
- `429 Too Many Requests` - Rate limit excedido

### Códigos de Erro do Servidor

- `500 Internal Server Error` - Erro interno do servidor
- `502 Bad Gateway` - Erro de gateway
- `503 Service Unavailable` - Serviço indisponível

---

## 💡 Exemplos Práticos

### 1. Fluxo Completo: Cliente Criando Necessidade

```javascript
// 1. Autenticação
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

// 2. Listar categorias
const categoriasResponse = await fetch('/api/v1/categorias/', {
    headers: {
        'Authorization': `Bearer ${access}`
    }
});

const categorias = await categoriasResponse.json();

// 3. Criar necessidade
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
    })
});

const necessidade = await necessidadeResponse.json();
```

### 2. Fornecedor Enviando Orçamento

```python
import requests

# Autenticação
auth_response = requests.post('https://indicaai.com/api/v1/auth/login/', json={
    'email': 'fornecedor@exemplo.com',
    'password': 'senha123'
})

token = auth_response.json()['access']
headers = {'Authorization': f'Bearer {token}'}

# Buscar necessidades ativas
necessidades = requests.get(
    'https://indicaai.com/api/v1/necessidades/?status=ativo',
    headers=headers
).json()

# Enviar orçamento
orcamento_data = {
    'necessidade': 123,
    'valor': 12500.00,
    'descricao': 'Proposta para reforma completa da cozinha...',
    'prazo_execucao': '2025-02-10',
    'observacoes': 'Inclui material e mão de obra'
}

orcamento_response = requests.post(
    'https://indicaai.com/api/v1/orcamentos/',
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

## 🛠️ SDKs e Bibliotecas

### JavaScript/TypeScript

```bash
npm install @indicaai/api-client
```

```javascript
import { IndicaiAPI } from '@indicaai/api-client';

const api = new IndicaiAPI({
    baseURL: 'https://indicaai.com/api/v1/',
    token: 'seu_jwt_token'
});

// Usar a API
const necessidades = await api.necessidades.list();
const novaAvaliacao = await api.avaliacoes.create(avaliacaoData);
```

### Python

```bash
pip install indicaai-api
```

```python
from indicaai_api import IndicaiClient

client = IndicaiClient(
    base_url='https://indicaai.com/api/v1/',
    token='seu_jwt_token'
)

# Usar a API
necessidades = client.necessidades.list()
nova_avaliacao = client.avaliacoes.create(avaliacao_data)
```

### React Native

```bash
npm install @indicaai/react-native-sdk
```

```javascript
import { useIndicaiAPI } from '@indicaai/react-native-sdk';

function MyComponent() {
    const { necessidades, loading, error } = useIndicaiAPI('necessidades');
    
    // Componente React Native
}
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

### v1.0.0 (2025-01-10)

- 🎉 Lançamento inicial da API
- ✅ Autenticação JWT implementada
- ✅ Sistema de permissões granular
- ✅ Documentação Swagger completa
- ✅ Rate limiting implementado
- ✅ 8 módulos principais disponíveis

---

**© 2025 Indicai. Todos os direitos reservados.**

*Esta documentação é mantida pela equipe de desenvolvimento da Indicai e é atualizada regularmente. Para sugestões ou correções, entre em contato através dos canais oficiais.*