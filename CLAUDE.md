# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Projeto Indicai

Sistema marketplace de necessidades desenvolvido em Django com API REST e funcionalidades de tempo real.

## Comandos Essenciais

### Desenvolvimento Local com Docker

```bash
# Configurar ambiente completo (primeira vez)
./setup_dev.sh

# Iniciar serviços
docker-compose -f docker-compose.dev.yml up -d

# Parar serviços
docker-compose -f docker-compose.dev.yml down

# Ver logs
docker-compose -f docker-compose.dev.yml logs -f

# Executar migrações
docker-compose -f docker-compose.dev.yml exec web python manage.py migrate

# Criar superusuário
docker-compose -f docker-compose.dev.yml exec web python manage.py createsuperuser

# Coletar arquivos estáticos
docker-compose -f docker-compose.dev.yml exec web python manage.py collectstatic --noinput

# Shell Django
docker-compose -f docker-compose.dev.yml exec web python manage.py shell

# Bash no container
docker-compose -f docker-compose.dev.yml exec web bash
```

### Desenvolvimento sem Docker

```bash
# Ativar ambiente virtual
source venv/bin/activate

# Instalar dependências
pip install -r requirements_dev.txt

# Executar migrações
python manage.py migrate

# Criar superusuário
python manage.py createsuperuser

# Coletar arquivos estáticos
python manage.py collectstatic --noinput

# Executar servidor de desenvolvimento
python manage.py runserver

# Shell Django
python manage.py shell
```

### Testes

```bash
# Executar todos os testes
python manage.py test

# Executar testes de um app específico
python manage.py test ads
python manage.py test api
python manage.py test budgets
```

### Celery (Tarefas Assíncronas)

```bash
# Worker
celery -A core worker -l info

# Beat (tarefas agendadas)
celery -A core beat -l info
```

## Arquitetura do Sistema

### Estrutura de Apps Django

O projeto segue a arquitetura MVT do Django com os seguintes apps principais:

- **ads/**: Sistema de anúncios/necessidades - gerencia criação, listagem e detalhes de necessidades
- **api/**: API REST com versionamento (v1) usando Django REST Framework e autenticação JWT
- **budgets/**: Sistema de orçamentos - propostas de fornecedores para necessidades
- **categories/**: Categorias e subcategorias de serviços/produtos
- **chat/**: Sistema de mensagens em tempo real usando WebSocket
- **core/**: Configurações centrais do Django, middlewares e context processors
- **notifications/**: Sistema de notificações para usuários
- **rankings/**: Sistema de avaliações e reputação entre usuários
- **search/**: Funcionalidades de busca e filtros
- **users/**: Autenticação customizada e perfis de usuário

### Configurações de Settings

O projeto usa configurações modulares em `core/settings/`:
- `base.py`: Configurações compartilhadas
- `dev.py`: Desenvolvimento local (DEBUG=True)
- `prod.py`: Produção

Variáveis de ambiente são carregadas de arquivos `.env.dev` ou `.env.prod`.

### Banco de Dados

PostgreSQL é usado em todos os ambientes. As credenciais são definidas via variáveis de ambiente:
- DB_NAME (ex: indicai_dev)
- DB_USER
- DB_PASSWORD
- DB_HOST
- DB_PORT

### Autenticação e API

- Autenticação JWT via `djangorestframework-simplejwt`
- API versionada em `/api/v1/`
- Documentação OpenAPI disponível em `/api/docs/`
- CORS configurado para desenvolvimento

### WebSocket e Tempo Real

- Chat em tempo real usando `python-socketio`
- Consumer em `chat/consumers.py`
- Redis como message broker

### Serviços Docker

O ambiente de desenvolvimento usa:
- **web**: Aplicação Django
- **db**: PostgreSQL 15
- **redis**: Cache e message broker
- **nginx**: Proxy reverso
- **celery**: Worker para tarefas assíncronas
- **celery-beat**: Scheduler para tarefas agendadas

### URLs Principais

- `/`: Homepage
- `/admin/`: Admin do Django
- `/api/v1/`: API REST
- `/api/docs/`: Documentação da API
- `/necessidades/`: Listagem de necessidades
- `/orcamentos/`: Sistema de orçamentos
- `/chat/`: Sistema de mensagens

### Arquivos Estáticos e Media

- Desenvolvimento: servidos pelo Django
- Produção: servidos pelo Nginx
- `STATIC_ROOT`: `/staticfiles/`
- `MEDIA_ROOT`: `/media/`