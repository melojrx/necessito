# Documentação da API Necessito

## Visão Geral

A API Necessito fornece acesso programático às principais funcionalidades do sistema Necessito, permitindo integrações com aplicações de terceiros. A API segue os princípios REST e utiliza JSON para formatação de dados.

## Autenticação

A API suporta autenticação via:
- Sessão (para uso no navegador)
- Autenticação básica (username/password)

Todas as requisições à API devem ser autenticadas, exceto para endpoints específicos marcados como públicos.

## Endpoints Disponíveis

### Usuários

- `GET /api/users/` - Lista todos os usuários
- `POST /api/users/` - Cria um novo usuário
- `GET /api/users/{id}/` - Obtém detalhes de um usuário específico
- `PUT /api/users/{id}/` - Atualiza um usuário existente
- `PATCH /api/users/{id}/` - Atualiza parcialmente um usuário existente
- `DELETE /api/users/{id}/` - Remove um usuário
- `GET /api/users/{id}/avaliacoes/` - Lista avaliações recebidas pelo usuário
- `GET /api/users/{id}/necessidades/` - Lista necessidades (anúncios) criados pelo usuário
- `GET /api/users/{id}/orcamentos/` - Lista orçamentos feitos pelo usuário (como fornecedor)

### Categorias

- `GET /api/categorias/` - Lista todas as categorias
- `POST /api/categorias/` - Cria uma nova categoria
- `GET /api/categorias/{id}/` - Obtém detalhes de uma categoria específica
- `PUT /api/categorias/{id}/` - Atualiza uma categoria existente
- `PATCH /api/categorias/{id}/` - Atualiza parcialmente uma categoria existente
- `DELETE /api/categorias/{id}/` - Remove uma categoria
- `GET /api/categorias/{id}/subcategorias/` - Lista subcategorias de uma categoria específica
- `GET /api/categorias/{id}/necessidades/` - Lista necessidades (anúncios) de uma categoria específica

### Subcategorias

- `GET /api/subcategorias/` - Lista todas as subcategorias
- `POST /api/subcategorias/` - Cria uma nova subcategoria
- `GET /api/subcategorias/{id}/` - Obtém detalhes de uma subcategoria específica
- `PUT /api/subcategorias/{id}/` - Atualiza uma subcategoria existente
- `PATCH /api/subcategorias/{id}/` - Atualiza parcialmente uma subcategoria existente
- `DELETE /api/subcategorias/{id}/` - Remove uma subcategoria
- `GET /api/subcategorias/{id}/necessidades/` - Lista necessidades (anúncios) de uma subcategoria específica

### Necessidades (Anúncios)

- `GET /api/necessidades/` - Lista todas as necessidades (anúncios)
- `POST /api/necessidades/` - Cria uma nova necessidade (anúncio)
- `GET /api/necessidades/{id}/` - Obtém detalhes de uma necessidade (anúncio) específica
- `PUT /api/necessidades/{id}/` - Atualiza uma necessidade (anúncio) existente
- `PATCH /api/necessidades/{id}/` - Atualiza parcialmente uma necessidade (anúncio) existente
- `DELETE /api/necessidades/{id}/` - Remove uma necessidade (anúncio)
- `GET /api/necessidades/{id}/orcamentos/` - Lista orçamentos de uma necessidade (anúncio) específica
- `GET /api/necessidades/{id}/avaliacoes/` - Lista avaliações de uma necessidade (anúncio) específica

### Orçamentos

- `GET /api/orcamentos/` - Lista todos os orçamentos
- `POST /api/orcamentos/` - Cria um novo orçamento
- `GET /api/orcamentos/{id}/` - Obtém detalhes de um orçamento específico
- `PUT /api/orcamentos/{id}/` - Atualiza um orçamento existente
- `PATCH /api/orcamentos/{id}/` - Atualiza parcialmente um orçamento existente
- `DELETE /api/orcamentos/{id}/` - Remove um orçamento

### Avaliações

- `GET /api/avaliacoes/` - Lista todas as avaliações
- `POST /api/avaliacoes/` - Cria uma nova avaliação
- `GET /api/avaliacoes/{id}/` - Obtém detalhes de uma avaliação específica
- `PUT /api/avaliacoes/{id}/` - Atualiza uma avaliação existente
- `PATCH /api/avaliacoes/{id}/` - Atualiza parcialmente uma avaliação existente
- `DELETE /api/avaliacoes/{id}/` - Remove uma avaliação

## Documentação Interativa

A API possui documentação interativa disponível nos seguintes endpoints:

- `/api/swagger/` - Interface Swagger UI
- `/api/redoc/` - Interface ReDoc

## Filtros e Busca

A maioria dos endpoints de listagem suporta filtragem e busca:

- Filtragem: `?campo=valor` (ex: `/api/necessidades/?status=ativo`)
- Busca: `?search=termo` (busca em campos relevantes)
- Ordenação: `?ordering=campo` (prefixo `-` para ordem descendente)

## Paginação

Todos os endpoints de listagem são paginados, retornando no máximo 10 itens por página. Para navegar entre as páginas, use o parâmetro `page`:

```
/api/necessidades/?page=2
```

## Exemplos de Uso

### Listar todas as categorias

```
GET /api/categorias/
```

### Criar um novo anúncio

```
POST /api/necessidades/
Content-Type: application/json

{
    "titulo": "Preciso de um eletricista",
    "descricao": "Instalação de tomadas e interruptores",
    "cliente": 1,
    "categoria": 3,
    "subcategoria": 12,
    "quantidade": 5,
    "unidade": "un"
}
```

### Buscar anúncios por termo

```
GET /api/necessidades/?search=eletricista
```

### Filtrar orçamentos por status

```
GET /api/orcamentos/?status=pendente
``` 