# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Projeto Necessito

Sistema marketplace B2B/B2C de necessidades desenvolvido em Django 5.1.4 com API REST, funcionalidades de tempo real e arquitetura de produção completa.

### Status do Projeto
- **Produção**: ✅ https://necessito.online (Totalmente Funcional)
- **Ambiente**: VPS Ubuntu com Docker + NGINX + SSL/TLS
- **CI/CD**: GitHub Actions automatizado
- **Deploy**: Zero downtime com health checks

## Comandos Essenciais

### Desenvolvimento Local com Docker (OTIMIZADO)

**Usando Makefile (Recomendado):**
```bash
# Ver todos os comandos disponíveis
make help

# Iniciar ambiente de desenvolvimento
make dev

# Parar serviços
make stop

# Ver logs em tempo real
make logs

# Executar migrações
make migrate

# Criar migrations
make makemigrations

# Criar superusuário
make createsuperuser

# Shell Django
make shell

# Executar testes
make test

# Iniciar com Celery worker (quando necessário)
make celery

# Limpar tudo (containers, volumes, networks)
make clean
```

**Usando Docker Compose diretamente:**
```bash
# Iniciar serviços (containers essenciais: db, redis, web)
docker compose -f docker-compose_dev.yml up -d

# Iniciar com Celery worker (opcional)
docker compose -f docker-compose_dev.yml --profile celery up -d

# Parar serviços
docker compose -f docker-compose_dev.yml down

# Ver logs
docker compose -f docker-compose_dev.yml logs -f

# Executar comando no container web
docker compose -f docker-compose_dev.yml exec necessito-web-dev python manage.py migrate
```

**Arquitetura de Desenvolvimento Simplificada:**
- ✅ **db**: PostgreSQL 15 (essencial)
- ✅ **redis**: Redis 7 (cache + broker Celery)
- ✅ **web**: Django com runserver (porta 8000)
- ⚡ **celery**: Worker opcional (use `--profile celery` quando necessário)

**Celery em Modo EAGER:**
- Por padrão, tasks Celery executam de forma **síncrona** (CELERY_TASK_ALWAYS_EAGER=True)
- Não requer worker rodando - ideal para desenvolvimento
- Para testar comportamento assíncrono real: `make celery` ou `--profile celery`

### Produção (VPS Ubuntu)

```bash
# Status dos containers em produção
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# Logs de produção
docker logs necessito-web_prod --tail 50 -f
docker logs nginx-global --tail 50 -f
docker logs nginx-necessito --tail 50 -f

# Deploy manual (caso necessário)
cd /root/necessito
set -a && source .env.prod && set +a
REGISTRY_IMAGE=necessito-web IMAGE_TAG=latest ./scripts/deploy.sh

# Verificar saúde da aplicação
curl -I https://necessito.online/health/
curl -I https://necessito.online

# Migrações em produção
docker-compose -f docker-compose_prod.yml exec web python manage.py migrate

# Backup manual do banco
./backup_postgres.sh

# Verificar certificados SSL
docker run --rm -v "/root/necessito/data/certbot/conf:/etc/letsencrypt" certbot/certbot certificates

# Renovar SSL manualmente
docker run --rm -v "/root/necessito/data/certbot/conf:/etc/letsencrypt" -v "/root/necessito/data/certbot/www:/var/www/certbot" certbot/certbot renew
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

PostgreSQL é usado em todos os ambientes:
- **Desenvolvimento**: PostgreSQL 15 (docker-compose.dev.yml)
- **Produção**: PostgreSQL 17 (VPS)

Credenciais são definidas via variáveis de ambiente:
- DB_NAME (ex: necessito_dev / necessito_prod)
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

**Desenvolvimento** (docker-compose_dev.yml - Otimizado):
- **db**: PostgreSQL 15-alpine (banco de dados)
- **redis**: Redis 7-alpine (cache + message broker)
- **web**: Django 5.1 com runserver (aplicação - porta 8000)
- **celery**: Worker Celery (opcional - use `--profile celery`)

**Produção** (docker-compose_prod.yml):
- **web**: necessito-web_prod (Django + Gunicorn)
- **db**: necessito-db_prod (PostgreSQL 17)
- **redis**: necessito-redis-prod (Redis 7-alpine)
- **nginx**: nginx-necessito (proxy interno)
- **celery**: necessito-celery-prod (worker)
- **celery-beat**: necessito-celery-beat-prod (scheduler)

**Infraestrutura Global**:
- **nginx-global**: Proxy SSL/TLS para todos os domínios

### URLs Principais

**Desenvolvimento** (http://localhost:8000):
- `/`: Homepage
- `/admin/`: Admin do Django
- `/api/v1/`: API REST
- `/api/docs/`: Documentação da API (Swagger/ReDoc)
- `/necessidades/`: Listagem de necessidades
- `/orcamentos/`: Sistema de orçamentos
- `/chat/`: Sistema de mensagens

**Produção** (https://necessito.online):
- `/`: Homepage (✅ Ativo)
- `/admin/`: Django Admin (✅ Ativo)
- `/api/v1/`: API REST Endpoints (✅ Ativo)
- `/api/docs/`: API Documentation (✅ Ativo)
- `/necessidades/`: Listagem de Necessidades (✅ Ativo)
- `/orcamentos/`: Sistema de Orçamentos (✅ Ativo)
- `/chat/`: Sistema de Mensagens (✅ Ativo)
- `/health/`: Health Check Endpoint (✅ Ativo)

### Arquivos Estáticos e Media

- **Desenvolvimento**: Servidos pelo Django dev server
- **Produção**: Servidos pelo Nginx com otimizações
- `STATIC_ROOT`: `/staticfiles/`
- `MEDIA_ROOT`: `/media/`

## 🚀 Deploy e CI/CD

### GitHub Actions Pipeline

Workflow automático configurado em `.github/workflows/ci-cd.yml`:

1. **Tests**: Testes automáticos em Python 3.12
2. **Build & Push**: Docker image para ghcr.io
3. **Deploy**: SSH para VPS com zero downtime

### Deploy Manual

```bash
# Em caso de necessidade de deploy manual
cd /root/necessito
set -a && source .env.prod && set +a

# Deploy com imagem específica
REGISTRY_IMAGE=necessito-web IMAGE_TAG=latest ./scripts/deploy.sh

# Rollback para versão anterior
./scripts/rollback.sh
```

## 🔒 Segurança e SSL

### Certificados SSL/TLS

- **Provedor**: Let's Encrypt
- **Domínios**: necessito.online, www.necessito.online
- **Renovação**: Automática via cron (00:00 e 12:00)
- **Validade**: Até 18/11/2025

### Headers de Segurança

Configurados no nginx-global:
- `Strict-Transport-Security`
- `X-Frame-Options: DENY`
- `X-Content-Type-Options: nosniff`
- `Referrer-Policy: same-origin`
- `X-XSS-Protection`

## 📊 Monitoramento e Logs

### Health Checks

```bash
# Verificar saúde da aplicação
curl -I https://necessito.online/health/
curl -I https://necessito.online

# Status dos containers
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
```

### Logs de Sistema

```bash
# Logs da aplicação Django
docker logs necessito-web_prod --tail 100 -f

# Logs do proxy NGINX
docker logs nginx-global --tail 50 -f
docker logs nginx-necessito --tail 50 -f

# Logs do Celery
docker logs necessito-celery-prod --tail 50 -f

# Logs de deploy
tail -f /root/necessito/logs/deploy.log

# Logs de backup
tail -f /root/necessito/logs/backup.log
```

### Backup e Recuperação

```bash
# Backup manual do PostgreSQL
./backup_postgres.sh

# Localização dos backups
ls -la /root/necessito/backups/

# Backup automático: Diariamente às 2:00 AM
# Retenção: 7 dias
# Formato: backup_YYYYMMDD_HHMMSS.sql.gz
```

## 🛠️ Troubleshooting

### Problemas Comuns

**502 Bad Gateway**:
```bash
# Verificar containers
docker ps | grep -E "nginx-global|nginx-necessito|necessito-web"

# Verificar conectividade
docker exec nginx-global ping -c 1 nginx-necessito
docker exec nginx-global curl -I http://nginx-necessito/health/
```

**SSL Issues**:
```bash
# Renovar certificados
docker run --rm -v "/root/necessito/data/certbot/conf:/etc/letsencrypt" -v "/root/necessito/data/certbot/www:/var/www/certbot" certbot/certbot renew --force-renewal

# Reiniciar nginx
docker restart nginx-global
```

**Container Issues**:
```bash
# Logs detalhados
docker logs [container_name] --details

# Recriar container
docker-compose -f docker-compose_prod.yml up -d --force-recreate [service_name]
```

## 📋 Arquivos de Configuração Importantes

- `docker-compose_dev.yml`: Ambiente de desenvolvimento (otimizado)
- `docker-compose_prod.yml`: Ambiente de produção
- `.env.dev` / `.env.prod`: Variáveis de ambiente
- `Makefile`: Comandos convenientes para desenvolvimento
- `ARQUITETURA_VPS_INTEGRACAO.md`: Documentação completa da infraestrutura
- `scripts/deploy.sh`: Script principal de deploy
- `nginx-global/conf/`: Configurações do NGINX global

## 🎯 Melhores Práticas de Desenvolvimento

### Ambiente de Desenvolvimento Otimizado

O ambiente de desenvolvimento foi otimizado seguindo as melhores práticas Django + Docker:

1. **Containers Essenciais**: Apenas o necessário (db, redis, web)
2. **Celery EAGER Mode**: Tasks executam de forma síncrona por padrão
3. **Hot Reload**: Código fonte montado como volume para reload automático
4. **Makefile**: Comandos convenientes e documentados
5. **Profile Celery**: Worker opcional via `--profile celery`
6. **Health Checks**: PostgreSQL e Redis com health checks configurados

### Fluxo de Trabalho Recomendado

```bash
# 1. Primeira vez - Iniciar ambiente
make dev

# 2. Aplicar migrations
make migrate

# 3. Criar superusuário
make createsuperuser

# 4. Acessar aplicação
# http://localhost:8000

# 5. Durante desenvolvimento - Ver logs
make logs

# 6. Quando necessário - Testar Celery real
make celery

# 7. Ao finalizar
make stop
```

### Estrutura de Arquivos

```
necessito/
├── docker-compose_dev.yml      # Docker Compose de desenvolvimento
├── docker-compose_prod.yml     # Docker Compose de produção
├── Makefile                    # Comandos convenientes
├── .env.dev                    # Variáveis de ambiente (dev)
├── .env.prod                   # Variáveis de ambiente (prod)
├── Dockerfile                  # Imagem Docker da aplicação
├── requirements_base.txt       # Dependências base
├── requirements_dev.txt        # Dependências de desenvolvimento
├── requirements_prod.txt       # Dependências de produção
├── manage.py                   # Django management
├── CLAUDE.md                   # Este arquivo
└── core/
    ├── settings/
    │   ├── base.py            # Settings compartilhados
    │   ├── dev.py             # Settings de desenvolvimento
    │   └── prod.py            # Settings de produção
    └── ...
```