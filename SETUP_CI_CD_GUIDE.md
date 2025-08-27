# 🚀 Guia de Configuração CI/CD - Necessito

**Status**: ✅ Implementação Completa  
**Versão**: 2.0 - Pipeline MVP com Digest Tracking  
**Data**: 26 de Agosto de 2025

## 📋 Resumo da Implementação

### ✅ Componentes Implementados

1. **Pipeline CI/CD Otimizado** (`.github/workflows/ci-cd.yml`)
   - Testes automatizados com PostgreSQL 17 + Redis 7
   - Build multi-stage com tracking por digest SHA-256
   - Deploy manual controlado via `workflow_dispatch`
   - Timeouts e concurrency groups configurados

2. **Scripts de Deploy Robustos**
   - `scripts/deploy.sh` - Deploy com rollback automático
   - `scripts/rollback.sh` - Rollback inteligente 
   - `scripts/migrate_collectstatic.sh` - Migrações seguras
   - Auditoria completa em `logs/deploy.log`

3. **Health Check Avançado**
   - Endpoint `/health/` com checks de DB, Cache e Disk
   - Headers de tracking (X-Commit-SHA, X-Environment)
   - Respostas JSON estruturadas para monitoramento

4. **Dockerfile Otimizado**
   - Multi-stage build reduzindo tamanho da imagem
   - Build args para GIT_COMMIT_SHA e BUILD_DATE
   - Healthcheck integrado e usuário não-root

5. **Segurança Implementada**
   - `.dockerignore` otimizado protegendo dados sensíveis
   - Lint com `ruff` e security scan com `bandit`
   - Headers de segurança no health check

## 🔑 Configuração de Secrets (GitHub)

### Secrets Necessários no GitHub Actions

Navegue para `Settings > Secrets and variables > Actions` no seu repositório GitHub e configure:

```bash
# SSH para deploy no VPS
SSH_KEY=-----BEGIN PRIVATE KEY-----
[sua chave privada SSH]
-----END PRIVATE KEY-----

SSH_HOST=31.97.17.10

SSH_USER=root
```

### Como Gerar a SSH Key (se necessário)

```bash
# No seu computador local
ssh-keygen -t ed25519 -C "github-actions@necessito"

# Copiar chave pública para o servidor
ssh-copy-id -i ~/.ssh/id_ed25519.pub root@31.97.17.10

# Copiar chave privada para GitHub Secret SSH_KEY
cat ~/.ssh/id_ed25519
```

## 🎯 Como Usar o Pipeline

### 1. Deploy Automático de Testes
```bash
# Qualquer push para main executa:
git push origin main
# ✅ Executará: tests → build → push (sem deploy)
```

### 2. Deploy Manual para Produção
```bash
# Via interface GitHub:
# 1. Vá para Actions → ci-cd workflow
# 2. Clique em "Run workflow" 
# 3. Deixe image_tag como "latest" (padrão)
# 4. Clique "Run workflow"

# ✅ Executará: deploy usando último digest → health check
```

### 3. Verificação Pós-Deploy
```bash
# Verificar saúde da aplicação
curl -I https://necessito.online/health/

# Ver logs de deploy no servidor
ssh root@31.97.17.10 "tail -f ~/necessito/logs/deploy.log"

# Status dos containers
ssh root@31.97.17.10 "docker ps --format 'table {{.Names}}\t{{.Status}}'"
```

## 📊 Monitoramento e Logs

### Logs de Auditoria
```bash
# Formato dos logs em logs/deploy.log:
2025-08-26T20:15:30 START sha256:abc123...
2025-08-26T20:16:45 OK sha256:abc123...

# Em caso de falha:
2025-08-26T20:17:20 FAIL sha256:def456... - health_check
2025-08-26T20:17:25 ROLLBACK sha256:def456... -> sha256:abc123...
```

### Health Check Response
```json
{
  "status": "healthy",
  "timestamp": "2025-08-26T20:15:30.123456",
  "commit_sha": "a1b2c3d4...",
  "build_date": "1234567890",
  "checks": {
    "database": "healthy",
    "cache": "healthy", 
    "disk_space": "healthy"
  },
  "django": {
    "debug": false,
    "database_engine": "django.db.backends.postgresql"
  }
}
```

## 🛠️ Comandos de Manutenção

### Deploy Manual (VPS)
```bash
cd /root/necessito
set -a && source .env.prod && set +a

# Deploy com digest específico (recomendado)
REGISTRY_IMAGE=ghcr.io/melojrx/necessito-web IMAGE_DIGEST=sha256:abc123... ./scripts/deploy.sh

# Deploy com tag (fallback)
REGISTRY_IMAGE=ghcr.io/melojrx/necessito-web IMAGE_TAG=latest ./scripts/deploy.sh
```

### Rollback Manual (VPS)
```bash
# Rollback automático (usa last_success_digest)
REGISTRY_IMAGE=ghcr.io/melojrx/necessito-web ./scripts/rollback.sh

# Rollback para digest específico
REGISTRY_IMAGE=ghcr.io/melojrx/necessito-web IMAGE_DIGEST=sha256:abc123... ./scripts/rollback.sh
```

### Debugging
```bash
# Ver digest atual em produção
cat /root/necessito/last_success_digest

# Ver logs de container
docker logs necessito-web_prod --tail 100

# Testar health check local
curl -v http://localhost:8000/health/

# Verificar imagem atual
docker ps --format "{{.Names}}: {{.Image}}" | grep necessito
```

## 🔍 Troubleshooting

### Pipeline Falha nos Testes
```bash
# Verificar localmente:
python manage.py check --deploy
python manage.py test --noinput
ruff check .
bandit -r . -ll
```

### Deploy Falha
```bash
# Verificar conectividade SSH
ssh root@31.97.17.10 "echo 'SSH OK'"

# Verificar se registry está acessível
docker pull ghcr.io/melojrx/necessito-web:latest

# Verificar logs de deploy
ssh root@31.97.17.10 "tail -20 ~/necessito/logs/deploy.log"
```

### Health Check Falha
```bash
# Verificar serviços
docker-compose -f docker-compose_prod.yml ps

# Verificar conectividade do banco
docker-compose -f docker-compose_prod.yml exec db pg_isready -U necessito_user -d necessito_prod

# Verificar Redis
docker-compose -f docker-compose_prod.yml exec redis redis-cli ping
```

## ✅ Checklist de Validação

### Pré-Requisitos
- [ ] Secrets configurados no GitHub (SSH_KEY, SSH_HOST, SSH_USER)
- [ ] VPS acessível via SSH
- [ ] Docker e docker-compose instalados no VPS
- [ ] Diretório `/root/necessito` existente no VPS
- [ ] Arquivo `.env.prod` configurado no VPS

### Validação do Pipeline
- [ ] Push para main executa testes e build
- [ ] Build gera digest e faz upload para GHCR
- [ ] Workflow dispatch executa deploy usando digest
- [ ] Health check retorna 200 com dados corretos
- [ ] Rollback funciona em caso de falha

### Validação da Aplicação
- [ ] https://necessito.online carrega corretamente
- [ ] https://necessito.online/health/ retorna JSON válido
- [ ] Logs de deploy são gerados em `logs/deploy.log`
- [ ] Arquivo `last_success_digest` é atualizado após deploy

## 🎉 Próximos Passos (Evolução)

1. **Notificações**: Slack/Email em caso de falha
2. **Cobertura**: Integração com Codecov
3. **Segurança**: Trivy scan noturno das imagens
4. **Blue/Green**: Deploy sem downtime duplicando serviços
5. **Métricas**: Prometheus + Grafana para monitoramento

---

## 📞 Suporte

**Documentação Completa**: `ARQUITETURA_VPS_INTEGRACAO.md`  
**Email**: suporteindicaai@hotmail.com  
**Repositório**: https://github.com/melojrx/necessito

---

*Pipeline implementado seguindo as melhores práticas de DevOps com foco em confiabilidade, auditoria e facilidade de manutenção.*