# 🏗️ Integração com Arquitetura VPS Multi-Aplicação

Este documento descreve como o projeto Necessito está integrado na arquitetura VPS Ubuntu que hospeda múltiplas aplicações.

## 📊 Visão Geral da Arquitetura

```
Internet (HTTPS/HTTP - Porta 80/443)
                    ↓
┌─────────────────────────────────────────────────────────────────────┐
│                        NGINX GLOBAL                                │
│                    (nginx-global)                                  │
│               Container: 315aca92d97b                              │
│           Rede: nginx-global_global-network                        │
│               Portas: 80/443 → SSL Termination                    │
│                                                                    │
│  ┌─────────────────────────┐    ┌─────────────────────────────────┐│
│  │   necessito.online      │    │   urbanlive.com.br             ││
│  │   ↓ proxy_pass          │    │   ↓ proxy_pass                 ││
│  │   nginx-necessito:80    │    │   urbanlive_web:8000           ││
│  └─────────────────────────┘    └─────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────────┘
         │                                    │
         ▼                                    ▼
┌───────────────────────────────┐    ┌────────────────────────────────┐
│      NECESSITO (Indicai)      │    │        URBANLIVE V2            │
│      🛒 Marketplace B2B       │    │    🏘️ Zeladoria Colaborativa   │
│                               │    │                                │
│ ┌───────────────────────────┐ │    │ ┌────────────────────────────┐ │
│ │ nginx-necessito           │ │    │ │ urbanlive_web              │ │
│ │ Container: nginx-necessito│ │    │ │ Container: 759c0de23534    │ │
│ │ Porta: 80 (interna)      │ │    │ │ Porta: 8000→8001 (externa) │ │
│ │ Redes: necessito_app_     │ │    │ │ Redes: engage_hub_default + │ │
│ │        network_prod +     │ │    │ │        global-network      │ │
│ │        nginx-global_      │ │    │ └────────────────────────────┘ │
│ │        global-network     │ │    │              ↓                │
│ └───────────────────────────┘ │    │ ┌────────────────────────────┐ │
│              ↓                │    │ │ Django 5.0.1 + DRF + JWT  │ │
│ ┌───────────────────────────┐ │    │ │ API REST + WebSocket       │ │
│ │ necessito-web_prod-1      │ │    │ └────────────────────────────┘ │
│ │ Container: necessito-web  │ │    │                                │
│ │ Porta: 8000 (interna)    │ │    │ ┌────────────────────────────┐ │
│ │ Rede: necessito_app_      │ │    │ │ urbanlive_db               │ │
│ │       network_prod        │ │    │ │ Container: e09300a390e4    │ │
│ └───────────────────────────┘ │    │ │ PostgreSQL 15-alpine       │ │
│              ↓                │    │ │ Porta: 5432→5433 (externa) │ │
│ ┌───────────────────────────┐ │    │ │ Rede: engage_hub_default   │ │
│ │ Django 5.1.4 + PostgreSQL│ │    │ └────────────────────────────┘ │
│ │ API REST + WebSocket     │ │    │                                │
│ └───────────────────────────┘ │    │ ┌────────────────────────────┐ │
│                               │    │ │ urbanlive_redis            │ │
│ ┌───────────────────────────┐ │    │ │ Container: d70cd237c622    │ │
│ │ necessito-db_prod-1       │ │    │ │ Redis 7-alpine             │ │
│ │ Container: necessito-db   │ │    │ │ Porta: 6379→6380 (externa) │ │
│ │ PostgreSQL 17            │ │    │ │ Rede: engage_hub_default   │ │
│ │ Porta: 5432 (externa)    │ │    │ └────────────────────────────┘ │
│ │ Rede: necessito_app_      │ │    └────────────────────────────────┘
│ │       network_prod        │ │
│ └───────────────────────────┘ │
└───────────────────────────────┘
```

## 🌐 Redes Docker

| **Rede** | **Função** | **Containers** |
|----------|------------|----------------|
| **nginx-global_global-network** | Comunicação global | nginx-global, nginx-necessito, urbanlive_web |
| **necessito_app_network_prod** | Rede interna Necessito | nginx-necessito, necessito-web_prod-1, necessito-db_prod-1 |
| **engage_hub_default** | Rede interna UrbanLive | urbanlive_web, urbanlive_db, urbanlive_redis |

## 🔌 Mapeamento de Portas

### Externas (VPS → Internet)
- **80/443** → nginx-global (HTTP/HTTPS + SSL)
- **5432** → necessito-db_prod-1 (PostgreSQL Necessito)
- **5433** → urbanlive_db (PostgreSQL UrbanLive)
- **6380** → urbanlive_redis (Redis UrbanLive)
- **8001** → urbanlive_web (Django UrbanLive)

### Internas (Container → Container)
- **nginx-global:80/443** → nginx-necessito:80, host:8001 (urbanlive)
- **nginx-necessito:80** → necessito-web_prod-1:8000
- **urbanlive_web:8000** → urbanlive_db:5432, urbanlive_redis:6379

## 🎯 URLs de Produção

- **Necessito (Indicai):** https://necessito.online → nginx-necessito:80 → necessito-web_prod-1:8000
- **UrbanLive V2:** https://urbanlive.com.br → host:8001 → urbanlive_web:8000

## 🔧 Configuração do Necessito

### Containers

| **Container** | **Nome** | **Função** | **Portas** | **Redes** |
|---------------|----------|------------|------------|----------|
| nginx-necessito | nginx-necessito | Proxy NGINX local | 80 (interna) | necessito_app_network_prod + nginx-global_global-network |
| necessito-web_prod-1 | necessito-web_prod-1 | Django App | 8000 (interna) | necessito_app_network_prod |
| necessito-db_prod-1 | necessito-db_prod-1 | PostgreSQL 17 | 5432 (externa) | necessito_app_network_prod |
| necessito-redis-prod | necessito-redis-prod | Redis Cache | 6379 (externa) | necessito_app_network_prod |
| necessito-celery-prod | necessito-celery-prod | Celery Worker | - | necessito_app_network_prod |
| necessito-celery-beat-prod | necessito-celery-beat-prod | Celery Beat | - | necessito_app_network_prod |

### Fluxo de Requisições

1. **Internet** → **nginx-global** (SSL termination)
2. **nginx-global** → **nginx-necessito:80** (proxy_pass)
3. **nginx-necessito** → **necessito-web_prod-1:8000** (Django)
4. **Django** → **necessito-db_prod-1:5432** (PostgreSQL)
5. **Django** → **necessito-redis-prod:6379** (Cache/Sessions)

## 🚀 Deploy e Manutenção

### Comandos Essenciais

```bash
# Verificar redes
docker network ls | grep nginx-global

# Verificar containers ativos
docker ps | grep necessito

# Logs do nginx-global
docker logs nginx-global

# Logs do nginx-necessito
docker logs nginx-necessito

# Deploy da aplicação
./deploy_prod.sh

# Verificar conectividade
docker exec nginx-necessito nginx -t
curl http://nginx-necessito/health/
```

### Troubleshooting

#### 502 Bad Gateway
1. Verificar se nginx-necessito está rodando
2. Verificar se necessito-web_prod-1 está respondendo na porta 8000
3. Verificar conectividade entre redes

#### SSL/HTTPS Issues
- SSL é gerenciado pelo nginx-global (container 315aca92d97b)
- Não configurar SSL no nginx-necessito
- Verificar configuração do proxy no nginx-global

#### Conectividade entre Aplicações
- Verificar se a rede nginx-global_global-network existe
- Verificar se nginx-necessito está conectado às duas redes
- Testar conectividade: `docker exec nginx-global ping nginx-necessito`

## 📋 Checklist de Integração

- [ ] Rede `nginx-global_global-network` existe e está ativa
- [ ] Container `nginx-global` está rodando e acessível
- [ ] Container `nginx-necessito` está conectado às duas redes
- [ ] Proxy configurado no nginx-global para `nginx-necessito:80`
- [ ] SSL/HTTPS gerenciado pelo nginx-global
- [ ] Aplicação Django respondendo em `necessito-web_prod-1:8000`
- [ ] Health check endpoint `/health/` funcionando
- [ ] Arquivos estáticos e mídia sendo servidos corretamente
- [ ] WebSockets funcionando para Django Channels

## 🔒 Segurança

### Responsabilidades

- **nginx-global**: SSL/TLS, HTTPS, certificados Let's Encrypt
- **nginx-necessito**: Headers de segurança, rate limiting, proxy reverso
- **Django**: Autenticação, autorização, validação de dados

### Headers de Segurança

Configurados no nginx-necessito:
- X-Frame-Options: DENY
- X-Content-Type-Options: nosniff
- X-XSS-Protection: 1; mode=block
- Referrer-Policy: strict-origin-when-cross-origin

### Rate Limiting

- API endpoints: 10 req/s com burst de 20
- Configurado no nginx-necessito para `/api/`

## 📊 Monitoramento

### Logs Importantes

```bash
# Nginx global (SSL, roteamento)
docker logs nginx-global

# Nginx necessito (proxy local)
docker logs nginx-necessito

# Django application
docker logs necessito-web_prod-1

# Database
docker logs necessito-db_prod-1
```

### Métricas

- **Uptime**: `docker ps | grep necessito`
- **Conectividade**: Health check em `/health/`
- **Performance**: Logs de acesso do nginx
- **Recursos**: `docker stats`

---

**Última atualização:** $(date)
**Versão da arquitetura:** VPS Ubuntu Multi-Aplicação v1.0