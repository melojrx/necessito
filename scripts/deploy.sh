#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'

# Deploy idempotente da aplicação Necessito.
# Pressupõe:
#  - docker compose plugin instalado
#  - arquivo docker-compose_prod.yml no diretório raiz
#  - .env.prod presente (não versionado)
#  - Imagens já publicadas no registry com tag SHA (passada via ENV IMAGE_TAG)
#  - Variável REGISTRY_IMAGE (ex: ghcr.io/org/necessito-web)

BLUE='\033[0;34m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; RED='\033[0;31m'; NC='\033[0m'
log(){ echo -e "${BLUE}[INFO]${NC} $*"; }
ok(){ echo -e "${GREEN}[OK]${NC} $*"; }
warn(){ echo -e "${YELLOW}[WARN]${NC} $*"; }
err(){ echo -e "${RED}[ERR]${NC} $*"; }

COMPOSE_FILE="docker-compose_prod.yml"
COMPOSE="docker compose -f $COMPOSE_FILE"

[[ -f $COMPOSE_FILE ]] || { err "Arquivo $COMPOSE_FILE não encontrado"; exit 1; }
[[ -f .env.prod ]] || { err "Arquivo .env.prod não encontrado"; exit 1; }

REGISTRY_IMAGE=${REGISTRY_IMAGE:-}
IMAGE_TAG=${IMAGE_TAG:-}
if [[ -z "$REGISTRY_IMAGE" || -z "$IMAGE_TAG" ]]; then
  err "Defina REGISTRY_IMAGE e IMAGE_TAG (ex: export REGISTRY_IMAGE=ghcr.io/org/necessito-web IMAGE_TAG=abcdef1)"; exit 1;
fi

log "Configurando variáveis de ambiente para imagens"
export REGISTRY_IMAGE="${REGISTRY_IMAGE}"
export IMAGE_TAG="${IMAGE_TAG}"

CURRENT_IMAGE_TAG="$(docker ps --format '{{.Names}} {{.Image}}' | awk '/necessito-web_prod/ {split($2, a, ":"); print a[length(a)]}')" || CURRENT_IMAGE_TAG=""
log "Tag atualmente em produção: ${CURRENT_IMAGE_TAG:-<desconhecida>}"

if [[ "${IMAGE_TAG}" == "${CURRENT_IMAGE_TAG}" ]]; then
  warn "A tag ${IMAGE_TAG} já está em produção. Prosseguindo mesmo assim (forçando recriação)."
fi

log "Pull das imagens (web, celery, celery-beat)"
$COMPOSE pull web celery celery-beat || true

log "Subindo dependências (db, redis) se ainda não estiverem ativas"
$COMPOSE up -d db redis

log "Executando migrações (imagem nova)"
$COMPOSE run --rm -e DJANGO_SETTINGS_MODULE=core.settings.prod web python manage.py migrate --noinput

log "Coletando estáticos"
$COMPOSE run --rm -e DJANGO_SETTINGS_MODULE=core.settings.prod web python manage.py collectstatic --noinput

log "Recriando serviços da aplicação (subindo em lote)"
$COMPOSE up -d web
sleep 2
$COMPOSE up -d celery celery-beat nginx

log "Verificando saúde (até 15 tentativas)"
HEALTH_URLS=("http://localhost:8000/health/" "http://localhost/health/" "https://necessito.online/health/")
for i in {1..15}; do
  for u in "${HEALTH_URLS[@]}"; do
    if curl -fsS "$u" >/dev/null 2>&1; then
      ok "Saúde OK em $u"
      echo "$IMAGE_TAG" > .last_successful_deploy
      echo "${REGISTRY_IMAGE}:${IMAGE_TAG}" > .last_successful_image
      exit 0
    fi
  done
  warn "Tentativa $i sem sucesso"; sleep 4
done
err "Aplicação não saudável após tentativas – iniciando rollback automático"
if [[ -f .last_successful_deploy ]]; then
  PREV=$(cat .last_successful_deploy)
  warn "Rollback para tag $PREV"
  REGISTRY_IMAGE="$REGISTRY_IMAGE" IMAGE_TAG="$PREV" bash scripts/rollback.sh || err "Rollback falhou"
else
  err "Sem tag anterior para rollback"
fi
exit 1
