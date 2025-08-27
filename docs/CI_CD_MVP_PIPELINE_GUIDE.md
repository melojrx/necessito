# Guia CI/CD MVP – Pipeline Enxuto e Replicável (Necessito)

Última atualização: 26/08/2025  
Status: Proposta pronta para implementação  
Escopo: Projeto Django (Necessito) – MVP mantido por 1 desenvolvedor Full Stack  
Ferramentas: GitHub Actions + Docker + Docker Compose + GHCR + VPS (Ubuntu)  
Público: Agente/CLI (ex: Claude Code CLI) executando tarefas de automação com zelo e profissionalismo.

---
## 🎯 Objetivos do Pipeline
| Objetivo | Descrição | Métrica Sucesso |
|----------|-----------|-----------------|
| Rapidez | Execução completa em < 6 min | Tempo médio último mês |
| Confiabilidade | Deploy só após testes + health | 0 quebras pós-deploy |
| Reprodutibilidade | Mesma imagem em build e produção (digest) | Digest registrado = deployado |
| Simplicidade | 1 arquivo workflow + 3–5 scripts | Manutenção < 30 min/mês |
| Segurança básica | Sem senhas versionadas, imagem reduzida | Sem vazamentos detectados |

---
## 🧱 Princípios
1. Imagens imutáveis por digest (não confiar apenas em `latest`).
2. Testes rápidos e determinísticos (sem retry manual “cego”).
3. Deploy controlado manual (workflow_dispatch) no estágio atual do MVP.
4. Rollback simples baseado em último digest válido.
5. Acoplamento mínimo: scripts de deploy independentes do workflow.

---
## 📦 Componentes do Pipeline
| Componente | Função | Arquivo / Local |
|------------|-------|-----------------|
| Workflow CI/CD | Orquestra test → build → deploy | `.github/workflows/ci-cd.yml` |
| `.dockerignore` | Reduz contexto / risco | Raiz do projeto |
| Scripts deploy | Automação Servidor | `scripts/deploy.sh` |
| Scripts rollback | Reversão rápida | `scripts/rollback.sh` |
| Migração + estáticos | Integridade pós-release | `scripts/migrate_collectstatic.sh` |
| Health check remoto | Verificação produção | `scripts/health_check.sh` (opcional) |
| Histórico digest | Auditoria & rollback | `last_success_digest` & `logs/deploy.log` |

---
## ✅ Escopo Inicial (Essencial)
1. Adicionar concurrency & timeouts ao workflow.
2. Ajustar job de testes para usar serviços `postgres` e `redis` internos.
3. Incluir `collectstatic` e `manage.py check` antes de rodar testes.
4. Lint + segurança leve: `ruff check` + `bandit`.
5. Construir imagem e publicar com tags `sha` e `latest` + registrar digest.
6. Deploy manual usando digest exportado (artefato) + scripts.
7. Health check remoto; rollback se falhar.
8. Registrar digest bem-sucedido.
9. Remover arquivo sensível `users.md` ou movê-lo para armazenamento seguro (NÃO versionar credenciais).

---
## 🛡️ Segurança Mínima
- Remover/criptografar `users.md` (contém senhas). Sugestão: `git rm users.md && echo 'REMOVIDO: contém credenciais' > SECURITY_NOTE.md`.
- Nunca armazenar `.env.prod` no repositório.
- Adicionar `.dockerignore` protegendo `media/`, `logs/`, `backups/`.

Exemplo `.dockerignore`:
```
.git
__pycache__/
*.pyc
media/
logs/
backups/
celerybeat-schedule
users.md
```

---
## 🧪 Estrutura do Job de Testes
Serviços: Postgres 17, Redis 7-alpine.  
Checks: migrations, static build, lint, security leve.

Razões: Garante coerência ambiente / produção e evita surpresa em runtime (ex: falta de coletstatic).

---
## 🏗️ Dockerfile (Multi-stage Simples – opcional inicial)
```
# syntax=docker/dockerfile:1
FROM python:3.11-slim AS builder
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends build-essential libpq-dev \
    && rm -rf /var/lib/apt/lists/*
COPY requirements_base.txt .
RUN pip install --upgrade pip && pip wheel --no-cache-dir -r requirements_base.txt -w /wheels

FROM python:3.11-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY --from=builder /wheels /wheels
RUN pip install --no-cache-dir /wheels/* && rm -rf /wheels
COPY . .
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser
EXPOSE 8000
CMD ["gunicorn", "core.wsgi:application", "--bind", "0.0.0.0:8000"]
```

---
## 🔁 Fluxo Operacional
1. Push em `main` → executa jobs test + build + push (SEM deploy automático).
2. Ao desejar publicar: acionar manual `workflow_dispatch` → job deploy usa último digest.
3. Servidor executa: pull digest → up services → migrations + static → health → registrar sucesso ou rollback.

---
## 🧾 Modelo de Workflow Proposto (Simplificado)
```
name: ci-cd

on:
  push:
    branches: [ main ]
  workflow_dispatch:
    inputs:
      image_tag:
        description: "Tag (default latest)"
        required: false
        default: "latest"

concurrency:
  group: ci-${{ github.ref }}
  cancel-in-progress: true

permissions:
  contents: read
  packages: write

env:
  PYTHON_VERSION: "3.11"
  REGISTRY_IMAGE: ghcr.io/${{ github.repository_owner }}/necessito-web

jobs:
  test:
    timeout-minutes: 15
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:17
        env:
          POSTGRES_USER: test
          POSTGRES_PASSWORD: test
          POSTGRES_DB: test
        options: >-
          --health-cmd="pg_isready -U test -d test" --health-interval=5s --health-timeout=5s --health-retries=5
      redis:
        image: redis:7-alpine
        options: >-
          --health-cmd="redis-cli ping" --health-interval=5s --health-timeout=5s --health-retries=5
    env:
      DJANGO_SETTINGS_MODULE: core.settings.dev
      DB_HOST: postgres
      DB_NAME: test
      DB_USER: test
      DB_PASSWORD: test
      REDIS_HOST: redis
    steps:
      - uses: actions/checkout@v4
      - name: Setup Python
        id: py
        uses: actions/setup-python@v5
        with: { python-version: ${{ env.PYTHON_VERSION }} }
      - name: Cache pip
        uses: actions/cache@v4
        with:
          path: ~/.cache/pip
          key: pip-${{ runner.os }}-py${{ steps.py.outputs.python-version }}-${{ hashFiles('requirements_*.txt') }}
      - name: Install deps
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements_base.txt
          pip install ruff bandit
      - name: Lint
        run: ruff check .
      - name: Security
        run: bandit -q -r .
      - name: Django checks
        run: python manage.py check
      - name: Migrate
        run: python manage.py migrate --noinput
      - name: Collectstatic
        run: python manage.py collectstatic --noinput
      - name: Tests
        run: python manage.py test --noinput

  build_push:
    timeout-minutes: 20
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Login GHCR
        uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.repository_owner }}
          password: ${{ secrets.GITHUB_TOKEN }}
      - name: Metadata
        id: meta
        uses: docker/metadata-action@v5
        with:
          images: ${{ env.REGISTRY_IMAGE }}
          tags: |
            type=sha
            type=raw,value=latest
      - name: Build & Push
        id: build
        uses: docker/build-push-action@v6
        with:
          context: .
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
      - name: Export digest
        run: echo "${{ steps.build.outputs.digest }}" > digest.txt
      - uses: actions/upload-artifact@v4
        with:
          name: image-digest
          path: digest.txt

  deploy:
    timeout-minutes: 10
    if: ${{ github.event_name == 'workflow_dispatch' }}
    needs: build_push
    runs-on: ubuntu-latest
    environment:
      name: production
      url: https://necessito.online
    steps:
      - uses: actions/download-artifact@v4
        with: { name: image-digest, path: . }
      - name: Read digest
        id: dig
        run: echo "DIGEST=$(cat digest.txt)" >> $GITHUB_OUTPUT
      - name: Check secrets
        run: |
          for s in SSH_KEY SSH_HOST SSH_USER; do [ -z "${{ secrets[s] }}" ] && echo "Missing $s" && exit 1 || true; done
      - name: Add SSH key
        uses: webfactory/ssh-agent@v0.9.0
        with: { ssh-private-key: ${{ secrets.SSH_KEY }} }
      - name: Known hosts
        run: ssh-keyscan -p 22 "${{ secrets.SSH_HOST }}" >> ~/.ssh/known_hosts
      - name: Deploy
        env:
          SSH_HOST: ${{ secrets.SSH_HOST }}
          SSH_USER: ${{ secrets.SSH_USER }}
          REGISTRY_IMAGE: ${{ env.REGISTRY_IMAGE }}
          IMAGE_DIGEST: ${{ steps.dig.outputs.DIGEST }}
        run: ssh $SSH_USER@$SSH_HOST "cd necessito && REGISTRY_IMAGE=$REGISTRY_IMAGE IMAGE_DIGEST=$IMAGE_DIGEST ./scripts/deploy.sh"
      - name: Remote health
        env:
          SSH_HOST: ${{ secrets.SSH_HOST }}
          SSH_USER: ${{ secrets.SSH_USER }}
        run: ssh $SSH_USER@$SSH_HOST "curl -fsS https://necessito.online/health/"
```

---
## 🧨 Scripts (Modelos)
### `scripts/deploy.sh`
```
#!/usr/bin/env bash
set -euo pipefail
: "${REGISTRY_IMAGE:?}" : "${IMAGE_DIGEST:?}"
LOG=logs/deploy.log
mkdir -p logs
DIGEST_SHORT=${IMAGE_DIGEST#sha256:}
echo "$(date -Iseconds) START $IMAGE_DIGEST" | tee -a $LOG

docker pull ${REGISTRY_IMAGE}@${IMAGE_DIGEST}
# Subir serviços principais
export IMAGE_TAG=$DIGEST_SHORT
# (Se compose usa variáveis, ajustar service para usar ${REGISTRY_IMAGE}@${IMAGE_DIGEST})

docker compose -f docker-compose_prod.yml up -d web celery celery-beat

./scripts/migrate_collectstatic.sh

if curl -fsS http://localhost:8000/health/ >/dev/null; then
  echo "$(date -Iseconds) OK $IMAGE_DIGEST" | tee -a $LOG
  echo "$IMAGE_DIGEST" > last_success_digest
else
  echo "$(date -Iseconds) FAIL $IMAGE_DIGEST" | tee -a $LOG
  ./scripts/rollback.sh || true
  exit 1
fi
```

### `scripts/migrate_collectstatic.sh`
```
#!/usr/bin/env bash
set -euo pipefail
python manage.py migrate --noinput
python manage.py collectstatic --noinput
```

### `scripts/rollback.sh`
```
#!/usr/bin/env bash
set -euo pipefail
: "${REGISTRY_IMAGE:?}"
if [ ! -f last_success_digest ]; then echo "Sem digest anterior"; exit 1; fi
DIGEST=$(cat last_success_digest)
echo "Rollback para $DIGEST"
docker pull ${REGISTRY_IMAGE}@${DIGEST}
docker compose -f docker-compose_prod.yml up -d web celery celery-beat
```

(Permissões: `chmod +x scripts/*.sh`.)

---
## 🩺 Health Endpoint
- Responder rápido (sem consultas pesadas).
- HTTP 200.
- Opcional: cabeçalho `X-Commit-SHA` configurado via middleware ou env.

---
## 📊 Métricas & Auditoria
Arquivo `logs/deploy.log` linhas exemplo:
```
2025-08-26T20:10:12 START sha256:abc123...
2025-08-26T20:10:45 OK sha256:abc123...
```
Rollback exemplo:
```
2025-08-27T09:02:11 START sha256:def456...
2025-08-27T09:02:40 FAIL sha256:def456...
2025-08-27T09:02:50 ROLLBACK sha256:abc123...
```

---
## 🚨 Itens Críticos Antes de Implantar
| Item | Ação |
|------|------|
| Remover credenciais versionadas | Apagar `users.md` |
| Secrets GitHub | Definir `SSH_KEY`, `SSH_HOST`, `SSH_USER` |
| Scripts executáveis | `chmod +x` |
| Health endpoint | Confirmar resposta 200 consistente |
| .dockerignore | Commitado |

---
## 🧪 Procedimento de Validação Local (Opcional)
1. Criar venv, instalar deps, rodar `manage.py check`.
2. Subir services com `docker compose -f docker-compose.dev.yml up -d db redis`.
3. Rodar migrations + tests.
4. Build local `docker build -t testimage:dev .`.
5. Rodar container local `docker run --rm -p 8000:8000 testimage:dev`.
6. Testar `/health/`.

---
## 🛠️ Passo a Passo para um Agente (Claude Code CLI)
| Passo | Descrição | Sucesso |
|-------|-----------|---------|
| 1 | Verificar ausência de credenciais sensíveis | Arquivo `users.md` removido |
| 2 | Criar `.dockerignore` | Arquivo presente com padrões | 
| 3 | Ajustar/Adicionar scripts | Scripts com permissão execução |
| 4 | Atualizar workflow conforme modelo | CI exibindo jobs test/build |
| 5 | Rodar pipeline em push de teste | Jobs concluídos sem erro |
| 6 | Disparar `workflow_dispatch` (staging) *se desejar* | Deploy executado |
| 7 | Confirmar health 200 | OK registrado no log |
| 8 | Simular falha (opcional) e testar rollback | Log mostra FAIL + rollback |
| 9 | Documentar digest em uso | `last_success_digest` presente |
| 10 | Encerrar com relatório sucinto | Resumo anexado |

---
## 🔮 Evolução Futuras (Quando houver tempo/tráfego)
- Trivy scan (imagem) nightly.
- Cobertura (pytest + coverage.xml + Codecov).
- Notificação Slack/Email em falha.
- Blue/Green simples duplicando serviço `web`.
- Job `schedule:` (cron) rebuild base image.

---
## ❗ Boas Práticas de Comunicação (para CLI)
- Logar cada etapa iniciada + sucesso/falha.
- Em erro: coletar últimas 100 linhas de logs relevantes (`web`, `nginx`).
- Nunca imprimir secrets ou conteúdo `.env`.
- Evitar loops de retry sem causa diagnosticada.

---
## ✅ Checklist Final de Implementação
```
[ ] Remover/segurar users.md
[ ] Adicionar .dockerignore
[ ] Criar scripts deploy/migrate/rollback
[ ] Tornar scripts executáveis
[ ] Atualizar workflow ci-cd.yml
[ ] Confirmar secrets no GitHub
[ ] Testar pipeline em push
[ ] Disparar deploy manual
[ ] Validar health + registrar digest
[ ] Documentar resultado (commit message / log)
```

---
## 🧾 Licença / Observações
Este guia é específico ao projeto Necessito (MVP). Ajuste nomes de imagens ou caminhos se portado para outra aplicação.

---
## 📌 Resumo Executivo
Pipeline lean focado em: testes determinísticos, build imutável por digest, deploy manual auditável, rollback rápido. Expansão futura preparada mas não imposta.

---
*FIM DO DOCUMENTO*
