# 🚀 Plano CI/CD Produção – Indicaai (Coexistindo com UrbanLive)

Este documento descreve, de forma prática e incremental, como implantar um pipeline de **build → teste → publicação → deploy** para o projeto **Indicaai**, compartilhando a mesma VPS onde já roda **UrbanLive**, sem causar indisponibilidade ou conflitos.

---
> NOTA SOBRE USO DE USUÁRIO: Neste momento os procedimentos serão executados como **usuário `root`** (decisão operacional atual). Em um hardening futuro recomenda-se criar um usuário não‑root (ex: `deploy`) pertencente ao grupo `docker` e remover acesso direto de root via SSH. As instruções abaixo já estão ajustadas para root.

## 📌 Objetivos
1. Deploy previsível e repetível usando imagens versionadas (tag por commit SHA).
2. Zero (ou mínimo) downtime em atualizações simples.
3. Convivência segura com a outra aplicação (Nginx global + redes isoladas).
4. Facilitar passagem de mudanças de `dev` para `prod` com um clique (dispatch) ou push em `main`.
5. Base para evoluir depois (blue/green, métricas, CDN, etc.).

---
## 🧱 Arquitetura Resumida (Produção)
```
Internet → NGINX GLOBAL (porta 80/443)
  ├─ necessito.online → nginx-necessito (rede nginx-global_global-network)
  │      → web (gunicorn) → db (PostgreSQL 17) / redis
  └─ urbanlive.com.br → urbanlive_web (já existente)
```
- **Isolamento:** Necessito usa rede interna `necessito_app_network_prod`; só o `nginx-necessito` participa também da `nginx-global_global-network`.
- **TLS/Certificados:** Gerenciados apenas no Nginx global (não duplicar no container local).

---
## 🗂️ Estrutura Recomendada de Arquivos (incremental)
| Caminho | Descrição |
|--------|-----------|
| `Dockerfile` | Multi-stage (fase posterior) / atual simples. |
| `docker-compose_prod.yml` | Orquestra DB, Redis, web, celery, nginx interno. |
| `scripts/deploy.sh` | Deploy idempotente usando imagem já publicada. |
| `scripts/migrate.sh` | Migrações isoladas. |
| `scripts/collectstatic.sh` | Coleta estáticos (se não embutido no build). |
| `scripts/rollback.sh` | Reverte para última tag saudável. |
| `scripts/backup_db.sh` | Gera dump rápido custom format. |
| `scripts/prune_images.sh` | Limpa imagens antigas. |
| `.env.prod` | Variáveis reais (NÃO versionado). |
| `.env.prod.example` | Modelo de referência (versionado). |
| `docs/CI_CD_PRODUCAO.md` | Este plano. |

---
## 🔐 Variáveis de Ambiente (Produção)
Arquivo de exemplo: `.env.prod.example` (já incluído). Copiar para `.env.prod` na VPS e ajustar valores.

Principais:
- Django/App: `DJANGO_SECRET_KEY`, `DJANGO_DEBUG=False`, `DJANGO_ALLOWED_HOSTS=necessito.online,www.necessito.online`
- Banco: `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`
- Redis / Celery: `REDIS_URL=redis://redis:6379/0`, `CELERY_BROKER_URL=redis://redis:6379/1`
- (Opcional) Observabilidade: `SENTRY_DSN`, `LOG_LEVEL=INFO`
- (Pipeline/deploy) `COMPOSE_PROJECT_NAME=necessito_prod`

> **Nunca** commit o `.env.prod`.

---
## 🛠️ Pipeline CI/CD (GitHub Actions – Visão)
### Gatilho
- Push / merge na branch `main` (automático) **OU** dispatch manual para tags/hotfix.

### Jobs
1. **test**
   - Checkout
   - Cache pip
   - Instala dependências
   - Executa testes (unitários / básicos)
2. **build_push** (depende de test)
   - Login no registry (GHCR ou Docker Hub privado)
   - `docker build` → tags: `${{ github.sha }}` e `latest`
   - Push
3. **deploy** (ambiente = production)
   - Executa via SSH na VPS:
     1. `export REGISTRY_IMAGE=... IMAGE_TAG=${{ github.sha }}`
     2. `./scripts/deploy.sh`
     3. Verifica saúde (`/health/`).
   - Em caso de falha: alerta + instrução para `scripts/rollback.sh`.

### Secrets / Vars Necessárias no GitHub
| Nome | Tipo | Uso |
|------|------|-----|
| `REGISTRY_USERNAME` | Secret | Login registry (se necessário) |
| `REGISTRY_TOKEN` | Secret | Token PAT / Access Token |
| `SSH_HOST` | Secret | IP ou hostname da VPS |
| `SSH_USER` | Secret | `root` (configuração atual – trocar futuramente para usuário restrito) |
| `SSH_PORT` | (opcional) Var | Porta SSH (default 22) |
| `SSH_KEY` | Secret | Chave privada (formato PEM) |
| `SENTRY_DSN` | Secret | (Opcional) monitoramento |

> **Banco / Redis creds não vão para Actions** – ficam somente em `.env.prod` na VPS (o container usa via `env_file`).

### Exemplo (Pseudo YAML Estruturado – será gerado depois)
```
name: ci-cd
on:
  push:
    branches: [ main ]
  workflow_dispatch:

jobs:
  test:
    runs-on: ubuntu-latest
    steps: [...]
  build_push:
    needs: test
    steps: [...]
  deploy:
    needs: build_push
    environment: production
    steps: [... ssh → ./scripts/deploy.sh ...]
```

---
## 🧪 Testes Antes do Build
Minimalista para começar:
- `python manage.py check`
- `python manage.py test` (ou subconjunto crítico)
- (Futuro) coverage + lint.

---
## 🔄 Fluxo de Deploy (scripts/deploy.sh)
1. Subir dependências (db, redis) se necessário.
2. Rodar migrações.
3. Rodar collectstatic.
4. Subir/recriar web, celery, celery-beat, nginx interno.
5. Health check (até 1 minuto). Marca `.last_successful_deploy`.

Se falhar → investigar logs ou `scripts/rollback.sh`.

---
## ♻️ Rollback
```
REGISTRY_IMAGE=ghcr.io/org/necessito-web ./scripts/rollback.sh
```
Reaponta `docker-compose_prod.yml` para última tag saudável registrada em `.last_successful_deploy` e sobe novamente.

---
## 🧰 Manutenção
| Ação | Comando |
|------|---------|
| Backup imediato | `./scripts/backup_db.sh` |
| Limpar imagens antigas | `REGISTRY_IMAGE=... ./scripts/prune_images.sh` |
| Migrações isoladas | `./scripts/migrate.sh` |
| Recoletar estáticos | `./scripts/collectstatic.sh` |

Agendar backup diário (cron na VPS):
```
0 2 * * * cd /caminho/app && ./scripts/backup_db.sh >> logs/backup.log 2>&1
```

---
## 🔐 Geração de Secrets (Exemplos)
### Chave Django
```
python -c 'import secrets, string; print("".join(secrets.choice(string.ascii_letters+string.digits+"!@#$%^&*(-_=+)") for _ in range(64)))'
```
### Senha Postgres
```
openssl rand -base64 32
```
### Criação no GitHub via CLI
```
# Exemplo (GitHub CLI)
gh secret set SSH_HOST --body "IP_DA_VPS"
gh secret set SSH_USER --body "deploy"
gh secret set SSH_KEY < ~/.ssh/id_rsa_deploy
```

---
## 🧩 Convivência com UrbanLive
| Aspecto | Requisito | Ação |
|---------|-----------|------|
| Portas externas | Evitar conflitos | Necessito não publica 8000/5432/6379 externamente. |
| Rede compartilhada | Nginx global | Apenas `nginx-necessito` entra na rede `nginx-global_global-network`. |
| TLS | Centralizado | Certificados só no Nginx global. |
| Segurança DB | Minimizar exposição | Remover `ports:` do Postgres / Redis (usar rede interna + túnel SSH). |

---
## 🛡️ Segurança Recomendada
- `SECURE_PROXY_SSL_HEADER=('HTTP_X_FORWARDED_PROTO','https')` (adicionar em settings prod).
- Remover/publicar somente se imprescindível: (5432, 6379) → preferir NÃO expor.
- Usuário Postgres diferente de `postgres` (futuro). 
- Fail2ban / UFW no host (fora do escopo do repo).

---
## 🧭 Acesso Seguro ao Banco via DBeaver
### 1. Sem exposição direta (preferido)
Na VPS (compose) **não** publicar porta do Postgres. Localmente (tunelando como root):
```
ssh -L 55432:localhost:5432 root@IP_DA_VPS -N
```
Configurar no DBeaver:
- Host: `localhost`
- Porta: `55432`
- Database: `necessito_prod`
- User / Password: conforme `.env.prod`

### 2. Usuário Read-Only (opcional)
```
CREATE ROLE analytics LOGIN PASSWORD 'SENHA_FORTE';
GRANT CONNECT ON DATABASE necessito_prod TO analytics;
GRANT USAGE ON SCHEMA public TO analytics;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO analytics;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO analytics;
```

### 3. Encerrar túnel
Ctrl+C no terminal que segura o SSH.

---
## 🧪 Health & Observabilidade (Base)
- Endpoint `/health/` já roteado.
- Próximo passo: adicionar exporter Prometheus ou Sentry (opcional).

---
## 📦 Evoluções Futuras (Roadmap)
| Fase | Item |
|------|------|
| 2 | Dockerfile multi-stage + coletar estáticos no build |
| 2 | Ajuste Nginx interno para suportar scale (upstream múltiplo) |
| 3 | Monitoramento central (Loki / Prometheus) |
| 3 | Backups automáticos + teste de restauração em staging |
| 4 | Blue/Green ou Canary |
| 4 | CDN (S3 + CloudFront) para estáticos e media |

---
## ✅ Checklist Execução Inicial (Modo root)
1. Criar secrets no GitHub: `SSH_HOST`, `SSH_USER=root`, `SSH_KEY` (chave privada que corresponde a `/root/.ssh/authorized_keys`).
2. Verificar que `docker-compose_prod.yml` não expõe Postgres/Redis (retirar qualquer bloco `ports:` desses serviços).
3. Copiar `.env.prod.example` → `.env.prod` em `/home/necessito` ou diretamente no diretório do projeto (ex: `/opt/necessito`).
4. (Opcional por agora) Ajustar firewall/UFW para liberar apenas 80/443/22.
5. Executar primeiro pipeline (ou manual: build da imagem + `./scripts/deploy.sh`).
6. Validar saúde: `curl -I https://necessito.online/health/` deve retornar `200`.
7. Confirmar acesso web e API (`/api/docs/`).
8. Ver logs iniciais: `docker compose -f docker-compose_prod.yml logs -n 50 web`.
9. Tag saudável gravada automaticamente em `.last_successful_deploy` após deploy OK.

### Guia Rápido: Primeiro Deploy Manual (root)
```
# 1. Clonar repositório
git clone <URL_DO_REPO> /opt/necessito
cd /opt/necessito

# 2. Criar arquivo de env
cp .env.prod.example .env.prod
vim .env.prod  # ajustar segredos

# 3. (Opcional) Pull de imagem já publicada
docker pull ghcr.io/<org>/necessito-web:latest

# 4. Deploy
REGISTRY_IMAGE=ghcr.io/<org>/necessito-web IMAGE_TAG=latest ./scripts/deploy.sh

# 5. Verificação
curl -I https://necessito.online/health/
```

> Depois de estabilizar o fluxo, planejar migração para usuário não-root.

---
## 🛠️ Comandos de Referência (Manual VPS)
```
# Deploy (já tendo imagem)
REGISTRY_IMAGE=ghcr.io/org/necessito-web IMAGE_TAG=<sha> ./scripts/deploy.sh

# Rollback
REGISTRY_IMAGE=ghcr.io/org/necessito-web ./scripts/rollback.sh

# Backup
./scripts/backup_db.sh

# Limpeza imagens
REGISTRY_IMAGE=ghcr.io/org/necessito-web KEEP=5 ./scripts/prune_images.sh
```

---
## 🧾 Notas Finais
- Manter este documento atualizado ao introduzir blue/green ou observabilidade.
- Evitar alterações manuais no compose em produção fora do fluxo.
- Sempre testar migrações disruptivas primeiro em staging.

---
**Fim do Plano CI/CD Produção – Necessito**
