# API Necessito

API RESTful para integração com o sistema Necessito, desenvolvida com Django Rest Framework.

## Estrutura da API

A API segue uma estrutura modular com os seguintes componentes:

- **Serializers**: Conversão de modelos Django para JSON e vice-versa
- **Views**: Class-Based Views (ViewSets) para manipulação de recursos
- **URLs**: Roteamento de endpoints
- **Permissões**: Controle de acesso aos recursos
- **Documentação**: Swagger/OpenAPI para documentação interativa

## Recursos Disponíveis

A API expõe os seguintes recursos:

- **Usuários**: Gerenciamento de usuários (clientes e fornecedores)
- **Categorias**: Categorias de produtos e serviços
- **Subcategorias**: Subcategorias de produtos e serviços
- **Necessidades**: Anúncios de necessidades dos clientes
- **Orçamentos**: Propostas de fornecedores para as necessidades
- **Avaliações**: Avaliações de clientes e fornecedores

## Instalação e Configuração

1. Adicione as dependências ao seu ambiente:

```bash
pip install -r requirements.txt
```

2. Configure o Django para usar a API:

```python
# settings.py
INSTALLED_APPS = [
    # ...
    'rest_framework',
    'drf_yasg',
    'django_filters',
    'api',
]
```

3. Adicione as URLs da API ao seu projeto:

```python
# urls.py
urlpatterns = [
    # ...
    path('api/', include('api.urls')),
]
```

## Autenticação

A API suporta autenticação via:

- Sessão (para uso no navegador)
- Autenticação básica (username/password)

## Documentação

A documentação completa da API está disponível em:

- `/api/swagger/`: Interface Swagger UI
- `/api/redoc/`: Interface ReDoc
- `/api/docs/`: Documentação em formato Markdown

## Exemplos de Uso

### Listar todas as categorias

```python
import requests

response = requests.get(
    'http://localhost:8000/api/categorias/',
    auth=('usuario@exemplo.com', 'senha')
)
categorias = response.json()
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
```

## Permissões

A API implementa um sistema de permissões para controlar o acesso aos recursos:

- **IsOwnerOrReadOnly**: Permite que apenas o proprietário de um objeto possa editá-lo
- **IsAdminOrReadOnly**: Permite que apenas administradores possam editar certos objetos

## Filtros e Busca

A maioria dos endpoints suporta filtragem e busca:

```
/api/necessidades/?status=ativo&search=eletricista
```