# Guia de Instalação e Uso da API Necessito

## Instalação

### 1. Dependências

Certifique-se de que as seguintes dependências estão instaladas:

```bash
pip install djangorestframework==3.15.1
pip install drf-yasg==1.21.7
pip install django-filter
```

Ou simplesmente execute:

```bash
pip install -r requirements.txt
```

### 2. Configuração do Django

Adicione as aplicações necessárias ao arquivo `settings.py`:

```python
INSTALLED_APPS = [
    # ...
    'rest_framework',
    'drf_yasg',
    'django_filters',
    'api',
]

# Configurações REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
    'DEFAULT_SCHEMA_CLASS': 'rest_framework.schemas.coreapi.AutoSchema',
}

# Configurações Swagger/OpenAPI
SWAGGER_SETTINGS = {
    'SECURITY_DEFINITIONS': {
        'Basic': {
            'type': 'basic'
        },
        'Bearer': {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header'
        }
    },
    'USE_SESSION_AUTH': True,
    'JSON_EDITOR': True,
    'VALIDATOR_URL': None,
}
```

### 3. Configuração das URLs

Adicione as URLs da API ao arquivo `urls.py` principal:

```python
urlpatterns = [
    # ...
    path('api/', include('api.urls')),
]
```

### 4. Migrações

Execute as migrações do Django:

```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Testes

Execute os testes para verificar se tudo está funcionando corretamente:

```bash
python manage.py test api
```

## Uso da API

### Autenticação

A API suporta autenticação via:

- Sessão (para uso no navegador)
- Autenticação básica (username/password)

Exemplo de autenticação básica com Python:

```python
import requests

# Autenticação básica
response = requests.get(
    'http://localhost:8000/api/categorias/',
    auth=('usuario@exemplo.com', 'senha')
)
```

### Endpoints Principais

- **Usuários**: `/api/users/`
- **Categorias**: `/api/categorias/`
- **Subcategorias**: `/api/subcategorias/`
- **Necessidades (Anúncios)**: `/api/necessidades/`
- **Orçamentos**: `/api/orcamentos/`
- **Avaliações**: `/api/avaliacoes/`

### Documentação Interativa

A documentação interativa da API está disponível em:

- `/api/swagger/`: Interface Swagger UI
- `/api/redoc/`: Interface ReDoc

### Filtros e Busca

A maioria dos endpoints suporta filtragem e busca:

- **Filtragem**: `?campo=valor` (ex: `/api/necessidades/?status=ativo`)
- **Busca**: `?search=termo` (busca em campos relevantes)
- **Ordenação**: `?ordering=campo` (prefixo `-` para ordem descendente)

### Paginação

Todos os endpoints de listagem são paginados, retornando no máximo 10 itens por página:

```
/api/necessidades/?page=2
```

## Exemplos de Uso

### Listar todas as categorias

```python
import requests

response = requests.get(
    'http://localhost:8000/api/categorias/',
    auth=('usuario@exemplo.com', 'senha')
)
categorias = response.json()
print(categorias)
```

### Criar um novo anúncio

```python
import requests

data = {
    "titulo": "Preciso de um eletricista",
    "descricao": "Instalação de tomadas e interruptores",
    "cliente": 1,
    "categoria": 3,
    "subcategoria": 12,
    "quantidade": 5,
    "unidade": "un"
}

response = requests.post(
    'http://localhost:8000/api/necessidades/',
    json=data,
    auth=('usuario@exemplo.com', 'senha')
)
anuncio = response.json()
print(anuncio)
```

### Buscar anúncios por termo

```python
import requests

response = requests.get(
    'http://localhost:8000/api/necessidades/?search=eletricista',
    auth=('usuario@exemplo.com', 'senha')
)
anuncios = response.json()
print(anuncios)
```

### Filtrar orçamentos por status

```python
import requests

response = requests.get(
    'http://localhost:8000/api/orcamentos/?status=pendente',
    auth=('usuario@exemplo.com', 'senha')
)
orcamentos = response.json()
print(orcamentos)
``` 