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

**Desenvolvimento** (docker-compose.dev.yml):
- **web**: Django 5.1.4 aplicação
- **db**: PostgreSQL 15
- **redis**: Redis 7 - cache e message broker
- **nginx**: Proxy reverso local
- **celery**: Worker para tarefas assíncronas
- **celery-beat**: Scheduler para tarefas agendadas

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

**Desenvolvimento** (http://localhost):
- `/`: Homepage
- `/admin/`: Admin do Django
- `/api/v1/`: API REST
- `/api/docs/`: Documentação da API
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

- `docker-compose.dev.yml`: Ambiente de desenvolvimento
- `docker-compose_prod.yml`: Ambiente de produção
- `.env.dev` / `.env.prod`: Variáveis de ambiente
- `ARQUITETURA_VPS_INTEGRACAO.md`: Documentação completa da infraestrutura
- `scripts/deploy.sh`: Script principal de deploy
- `nginx-global/conf/`: Configurações do NGINX global