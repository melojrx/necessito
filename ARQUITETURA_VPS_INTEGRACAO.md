# 🏗️ Arquitetura VPS Multi-Aplicação - Documentação Completa

**Última atualização:** 20 de Agosto de 2025  
**Versão:** 2.0 - Produção Completa com SSL e CI/CD  
**Status:** ✅ **TOTALMENTE FUNCIONAL**

## 📊 Visão Geral da Arquitetura

Esta VPS Ubuntu (31.97.17.10) hospeda duas aplicações Django independentes, orquestradas por um NGINX global que gerencia SSL/TLS e proxy reverso.

```
Internet (HTTPS/443 | HTTP/80)
            ↓
┌─────────────────────────────────────────────────────────────────────────┐
│                         NGINX GLOBAL (SSL/TLS)                          │
│                     Container: nginx-global                             │
│                 Rede: nginx-global_global-network                       │
│              Certificados Let's Encrypt (Válidos até 18/11/2025)       │
│                                                                         │
│  ┌──────────────────────────┐    ┌───────────────────────────────────┐ │
│  │   necessito.online       │    │   urbanlive.com.br               │ │
│  │   www.necessito.online   │    │   www.urbanlive.com.br           │ │
│  │                          │    │                                  │ │
│  │   proxy_pass →           │    │   proxy_pass →                   │ │
│  │   nginx-necessito:80     │    │   urbanlive_web:8000             │ │
│  └──────────────────────────┘    └───────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────┘
            │                                    │
            ▼                                    ▼
┌────────────────────────────────┐    ┌──────────────────────────────────┐
│       NECESSITO APP            │    │        URBANLIVE APP             │
│   🛒 Marketplace B2B/B2C       │    │   🏘️ Zeladoria Colaborativa      │
│                                │    │                                  │
│ ┌────────────────────────────┐ │    │ ┌──────────────────────────────┐ │
│ │ nginx-necessito            │ │    │ │ urbanlive_web                │ │
│ │ Container Nginx interno    │ │    │ │ Django 5.0.1 + DRF + JWT    │ │
│ │ Porta: 80 (interna)       │ │    │ │ Porta: 8000 (interna)       │ │
│ └────────────────────────────┘ │    │ └──────────────────────────────┘ │
│              ↓                 │    │              ↓                   │
│ ┌────────────────────────────┐ │    │ ┌──────────────────────────────┐ │
│ │ necessito-web_prod         │ │    │ │ urbanlive_db                 │ │
│ │ Django 5.1.4 + Gunicorn   │ │    │ │ PostgreSQL 15-alpine         │ │
│ │ Porta: 8000 (interna)     │ │    │ │ Porta: 5432 (interna)       │ │
│ └────────────────────────────┘ │    │ └──────────────────────────────┘ │
│              ↓                 │    │              ↓                   │
│ ┌────────────────────────────┐ │    │ ┌──────────────────────────────┐ │
│ │ necessito-db_prod          │ │    │ │ urbanlive_redis              │ │
│ │ PostgreSQL 17              │ │    │ │ Redis 7-alpine               │ │
│ │ Porta: 5432 (interna)     │ │    │ │ Porta: 6379 (interna)       │ │
│ └────────────────────────────┘ │    │ └──────────────────────────────┘ │
│                                │    │                                  │
│ ┌────────────────────────────┐ │    │                                  │
│ │ necessito-redis-prod       │ │    │                                  │
│ │ Redis 7-alpine             │ │    │                                  │
│ │ Porta: 6379 (interna)     │ │    │                                  │
│ └────────────────────────────┘ │    │                                  │
│                                │    │                                  │
│ ┌────────────────────────────┐ │    │                                  │
│ │ necessito-celery-prod      │ │    │                                  │
│ │ Celery Worker              │ │    │                                  │
│ └────────────────────────────┘ │    │                                  │
│                                │    │                                  │
│ ┌────────────────────────────┐ │    │                                  │
│ │ necessito-celery-beat-prod │ │    │                                  │
│ │ Celery Beat Scheduler      │ │    │                                  │
│ └────────────────────────────┘ │    │                                  │
└────────────────────────────────┘    └──────────────────────────────────┘
```

## 🌐 Redes Docker

### Configuração de Redes

| **Rede** | **Tipo** | **Função** | **Containers Conectados** |
|----------|----------|------------|---------------------------|
| **nginx-global_global-network** | Bridge | Comunicação entre proxy e apps | nginx-global, nginx-necessito, urbanlive_web |
| **necessito_prod_necessito_app_network_prod** | Bridge | Rede interna Necessito | nginx-necessito, necessito-web_prod, necessito-db_prod, necessito-redis-prod, celery containers |
| **engage_hub_default** | Bridge | Rede interna UrbanLive | urbanlive_web, urbanlive_db, urbanlive_redis |

### Verificação de Conectividade

```bash
# Listar todas as redes
docker network ls

# Inspecionar rede global
docker network inspect nginx-global_global-network

# Verificar conectividade
docker exec nginx-global ping -c 1 nginx-necessito
docker exec nginx-global ping -c 1 urbanlive_web
```

## 🔌 Mapeamento de Portas

### Portas Expostas Externamente (VPS → Internet)

| **Porta** | **Serviço** | **Protocolo** | **Descrição** |
|-----------|-------------|---------------|---------------|
| 80 | nginx-global | HTTP | Redirecionamento para HTTPS |
| 443 | nginx-global | HTTPS | Tráfego SSL/TLS |

### Portas Internas (Container → Container)

| **Serviço** | **Porta Interna** | **Rede** | **Acessível Por** |
|-------------|-------------------|----------|-------------------|
| nginx-necessito | 80 | global-network | nginx-global |
| necessito-web_prod | 8000 | necessito_app_network | nginx-necessito |
| necessito-db_prod | 5432 | necessito_app_network | necessito-web_prod |
| necessito-redis-prod | 6379 | necessito_app_network | necessito-web_prod, celery |
| urbanlive_web | 8000 | global-network + engage_hub | nginx-global |
| urbanlive_db | 5432 | engage_hub_default | urbanlive_web |
| urbanlive_redis | 6379 | engage_hub_default | urbanlive_web |

## 🔐 Certificados SSL/TLS

### Configuração Let's Encrypt

```bash
# Localização dos certificados
/root/necessito/data/certbot/conf/live/necessito.online/
├── fullchain.pem    # Certificado completo
├── privkey.pem      # Chave privada
├── cert.pem         # Certificado do domínio
└── chain.pem        # Cadeia de certificação

/root/necessito/data/certbot/conf/live/urbanlive.com.br/
├── fullchain.pem
├── privkey.pem
├── cert.pem
└── chain.pem

# Arquivos de configuração SSL
/root/necessito/data/certbot/conf/options-ssl-nginx.conf
/root/necessito/data/certbot/conf/ssl-dhparams.pem
```

### Renovação de Certificados

```bash
# Renovação automática via cron (já configurado)
0 0,12 * * * docker run --rm \
  -v "/root/necessito/data/certbot/conf:/etc/letsencrypt" \
  -v "/root/necessito/data/certbot/www:/var/www/certbot" \
  certbot/certbot renew --quiet

# Renovação manual
docker run --rm \
  -v "/root/necessito/data/certbot/conf:/etc/letsencrypt" \
  -v "/root/necessito/data/certbot/www:/var/www/certbot" \
  certbot/certbot renew

# Verificar status dos certificados
docker run --rm \
  -v "/root/necessito/data/certbot/conf:/etc/letsencrypt" \
  certbot/certbot certificates
```

## 🎯 URLs de Produção e Endpoints

### Necessito (Marketplace)

| **URL** | **Descrição** | **Status** |
|---------|---------------|------------|
| https://necessito.online | Homepage | ✅ Ativo |
| https://www.necessito.online | Homepage (www) | ✅ Ativo |
| https://necessito.online/admin/ | Django Admin | ✅ Ativo |
| https://necessito.online/api/docs/ | API Documentation | ✅ Ativo |
| https://necessito.online/api/v1/ | API REST Endpoints | ✅ Ativo |
| https://necessito.online/necessidades/ | Listagem de Necessidades | ✅ Ativo |
| https://necessito.online/orcamentos/ | Sistema de Orçamentos | ✅ Ativo |

### UrbanLive (Zeladoria)

| **URL** | **Descrição** | **Status** |
|---------|---------------|------------|
| https://urbanlive.com.br | Homepage | ✅ Ativo |
| https://www.urbanlive.com.br | Homepage (www) | ✅ Ativo |
| https://urbanlive.com.br/admin/ | Django Admin | ✅ Ativo |
| https://urbanlive.com.br/api/docs/ | API Documentation | ✅ Ativo |
| https://urbanlive.com.br/api/v1/ | API REST Endpoints | ✅ Ativo |
| https://urbanlive.com.br/contas/login/ | Sistema de Login | ✅ Ativo |

## 📦 Configuração dos Containers

### Necessito Containers

```yaml
# docker-compose_prod.yml summary
services:
  db:
    image: postgres:17
    container_name: necessito-db_prod
    environment:
      POSTGRES_DB: necessito_prod
      POSTGRES_USER: necessito_user
    networks:
      - necessito_app_network_prod

  redis:
    image: redis:7-alpine
    container_name: necessito-redis-prod
    networks:
      - necessito_app_network_prod

  web:
    image: necessito-web:local  # ou ghcr.io/melojrx/necessito-web:latest
    container_name: necessito-web_prod
    command: gunicorn core.wsgi:application --bind 0.0.0.0:8000
    depends_on:
      - db
      - redis
    networks:
      - necessito_app_network_prod

  celery:
    image: necessito-web:local
    container_name: necessito-celery-prod
    command: celery -A core worker -l info
    networks:
      - necessito_app_network_prod

  celery-beat:
    image: necessito-web:local
    container_name: necessito-celery-beat-prod
    command: celery -A core beat -l info
    networks:
      - necessito_app_network_prod

  nginx:
    image: nginx:alpine
    container_name: nginx-necessito
    networks:
      - necessito_app_network_prod
      - nginx-global_global-network
```

### UrbanLive Containers

```yaml
# docker-compose.yml summary (engage_hub)
services:
  db:
    image: postgres:15-alpine
    container_name: urbanlive_db
    environment:
      POSTGRES_DB: engagehub_prod
      POSTGRES_USER: engagehub_user
    networks:
      - engage_hub_default

  redis:
    image: redis:7-alpine
    container_name: urbanlive_redis
    networks:
      - engage_hub_default

  web:
    image: urbanlive_web
    container_name: urbanlive_web
    command: gunicorn core.wsgi:application --bind 0.0.0.0:8000
    networks:
      - engage_hub_default
      - nginx-global_global-network
```

## 🚀 CI/CD Pipeline

### GitHub Actions Workflow

```yaml
# .github/workflows/ci-cd.yml
name: ci-cd
on:
  push:
    branches: [ main ]
  workflow_dispatch:

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - Checkout
      - Setup Python
      - Run tests
      
  build_push:
    needs: test
    steps:
      - Build Docker image
      - Push to ghcr.io
      
  deploy:
    needs: build_push
    environment: production
    steps:
      - SSH to VPS
      - Run deploy script
      - Health check
```

### Scripts de Deploy

| **Script** | **Localização** | **Função** |
|------------|-----------------|------------|
| deploy.sh | /root/necessito/scripts/ | Deploy principal com zero downtime |
| migrate.sh | /root/necessito/scripts/ | Executa migrações do banco |
| collectstatic.sh | /root/necessito/scripts/ | Coleta arquivos estáticos |
| rollback.sh | /root/necessito/scripts/ | Reverte para última versão estável |
| backup_db.sh | /root/necessito/scripts/ | Backup do PostgreSQL |
| backup_postgres.sh | /root/necessito/ | Backup automático (cron) |

### Backup Automático

```bash
# Configuração do crontab
0 2 * * * /root/necessito/backup_postgres.sh >> /root/necessito/logs/backup.log 2>&1

# Script de backup
#!/bin/bash
BACKUP_DIR="/root/necessito/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
docker compose -f docker-compose_prod.yml exec -T db \
  pg_dump -U necessito_user necessito_prod > "$BACKUP_DIR/backup_$TIMESTAMP.sql"
gzip "$BACKUP_DIR/backup_$TIMESTAMP.sql"
find "$BACKUP_DIR" -name "*.sql.gz" -mtime +7 -delete
```

## 🛠️ Comandos de Manutenção

### Verificação de Status

```bash
# Status geral dos containers
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# Verificar logs
docker logs nginx-global --tail 50
docker logs nginx-necessito --tail 50
docker logs necessito-web_prod --tail 50
docker logs urbanlive_web --tail 50

# Verificar consumo de recursos
docker stats --no-stream

# Testar conectividade HTTPS
curl -I https://necessito.online
curl -I https://urbanlive.com.br
```

### Deploy Manual

```bash
# Deploy Necessito
cd /root/necessito
set -a && source .env.prod && set +a
REGISTRY_IMAGE=necessito-web IMAGE_TAG=latest ./scripts/deploy.sh

# Deploy UrbanLive
cd /root/engage_hub
docker-compose down && docker-compose up -d
```

### Troubleshooting

#### Problema: 502 Bad Gateway

```bash
# Verificar se containers estão rodando
docker ps | grep -E "nginx-global|nginx-necessito|necessito-web|urbanlive_web"

# Verificar conectividade de rede
docker exec nginx-global ping -c 1 nginx-necessito
docker exec nginx-global curl -I http://nginx-necessito/health/

# Verificar logs de erro
docker logs nginx-global --tail 100 | grep error
docker logs nginx-necessito --tail 100 | grep error
```

#### Problema: Certificado SSL Expirado

```bash
# Renovar certificados manualmente
docker run --rm \
  -v "/root/necessito/data/certbot/conf:/etc/letsencrypt" \
  -v "/root/necessito/data/certbot/www:/var/www/certbot" \
  certbot/certbot renew --force-renewal

# Reiniciar nginx-global
docker restart nginx-global
```

#### Problema: Container não inicia

```bash
# Verificar logs detalhados
docker logs [container_name] --details

# Verificar configuração
docker compose -f docker-compose_prod.yml config

# Recriar container
docker compose -f docker-compose_prod.yml up -d --force-recreate [service_name]
```

## 🔒 Segurança

### Headers de Segurança (nginx-global)

```nginx
# Configurados em /root/nginx-global/conf/test_ssl.conf
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;
add_header X-Frame-Options "DENY" always;
add_header X-Content-Type-Options "nosniff" always;
add_header Referrer-Policy "same-origin" always;
add_header X-XSS-Protection "1; mode=block" always;
```

### Firewall (UFW)

```bash
# Configuração recomendada
ufw default deny incoming
ufw default allow outgoing
ufw allow 22/tcp    # SSH
ufw allow 80/tcp    # HTTP
ufw allow 443/tcp   # HTTPS
ufw enable
```

### Credenciais e Variáveis de Ambiente

- Arquivos `.env.prod` nunca devem ser versionados
- Senhas fortes geradas com 32+ caracteres
- Rotação de credenciais a cada 90 dias recomendada
- Backup seguro das credenciais em local externo

## 📊 Monitoramento

### Health Checks

```bash
# Script de monitoramento
#!/bin/bash
check_service() {
    local url=$1
    local name=$2
    if curl -fsS "$url" > /dev/null 2>&1; then
        echo "✅ $name está funcionando"
    else
        echo "❌ $name está com problema"
    fi
}

check_service "https://necessito.online/health/" "Necessito"
check_service "https://urbanlive.com.br/api/health/" "UrbanLive"
```

### Logs Centralizados

```bash
# Diretórios de logs
/root/necessito/logs/          # Logs do Necessito
/root/engage_hub/logs/         # Logs do UrbanLive
/var/log/letsencrypt/          # Logs do Certbot

# Tail em tempo real
tail -f /root/necessito/logs/django.log
tail -f /root/engage_hub/logs/django.log
```

## 📋 Checklist de Validação

### ✅ Infraestrutura
- [x] VPS Ubuntu configurada
- [x] Docker e Docker Compose instalados
- [x] Redes Docker criadas e conectadas
- [x] Firewall configurado

### ✅ Aplicação Necessito
- [x] Containers rodando (web, db, redis, celery)
- [x] nginx-necessito configurado
- [x] Migrações aplicadas
- [x] Estáticos coletados
- [x] HTTPS funcionando
- [x] Admin acessível

### ✅ Aplicação UrbanLive
- [x] Containers rodando (web, db, redis)
- [x] Proxy direto do nginx-global
- [x] Migrações aplicadas
- [x] HTTPS funcionando
- [x] Admin acessível

### ✅ SSL/TLS
- [x] Certificados Let's Encrypt válidos
- [x] Renovação automática configurada
- [x] Headers de segurança implementados
- [x] HSTS habilitado

### ✅ CI/CD
- [x] GitHub Actions configurado
- [x] Scripts de deploy funcionais
- [x] Backup automático agendado
- [x] Rollback testado

## 🔄 Processo de Atualização

### 1. Desenvolvimento Local
```bash
# Branch de feature
git checkout -b feature/nova-funcionalidade
# Desenvolvimento e testes
git add . && git commit -m "feat: nova funcionalidade"
git push origin feature/nova-funcionalidade
```

### 2. Pull Request
- Criar PR no GitHub
- Code review
- Testes automáticos via CI

### 3. Deploy Automático
```bash
# Merge para main
git checkout main
git merge feature/nova-funcionalidade
git push origin main
# GitHub Actions executa deploy automaticamente
```

### 4. Verificação Pós-Deploy
```bash
# Verificar saúde
curl -I https://necessito.online/health/
# Verificar logs
docker logs necessito-web_prod --tail 100
# Testar funcionalidade
```

## 📝 Notas Importantes

1. **Isolamento**: Cada aplicação tem sua própria rede interna
2. **SSL**: Gerenciado centralmente pelo nginx-global
3. **Backup**: Executado diariamente às 2:00 AM
4. **Logs**: Rotacionados automaticamente para evitar estouro de disco
5. **Monitoramento**: Health checks disponíveis para ambas aplicações
6. **Segurança**: Headers de segurança e HSTS configurados

## 🆘 Suporte e Contatos

- **Documentação Necessito**: `/root/necessito/docs/`
- **Documentação UrbanLive**: `/root/engage_hub/docs/`
- **Logs de Deploy**: `/root/necessito/logs/deploy.log`
- **Email Suporte**: suporteindicaai@hotmail.com

---

**Última verificação de funcionamento:** 20 de Agosto de 2025 - 23:00  
**Próxima renovação SSL:** 18 de Novembro de 2025  
**Versão do documento:** 2.0