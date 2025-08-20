#!/usr/bin/env bash
set -euo pipefail

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
COMPOSE="docker compose"

[[ -f $COMPOSE_FILE ]] || { err "Arquivo $COMPOSE_FILE não encontrado"; exit 1; }
[[ -f .env.prod ]] || { err "Arquivo .env.prod não encontrado"; exit 1; }

REGISTRY_IMAGE=${REGISTRY_IMAGE:-}
IMAGE_TAG=${IMAGE_TAG:-}
if [[ -z "$REGISTRY_IMAGE" || -z "$IMAGE_TAG" ]]; then
  err "Defina REGISTRY_IMAGE e IMAGE_TAG (ex: export REGISTRY_IMAGE=ghcr.io/org/necessito-web IMAGE_TAG=abcdef1)"; exit 1;
fi

log "Atualizando imagens (${REGISTRY_IMAGE}:${IMAGE_TAG})"
if grep -q 'build: .' "$COMPOSE_FILE"; then
  sed -i.bak \
    -e "s|build: .|image: ${REGISTRY_IMAGE}:${IMAGE_TAG}|" \
    -e "s|container_name: necessito-web_prod-1|container_name: necessito-web_prod|" \
    $COMPOSE_FILE
fi

log "Pull da imagem"
$COMPOSE pull web || true

log "Subindo dependências (db, redis) se ainda não estiverem ativas"
$COMPOSE up -d db redis

log "Executando migrações"
$COMPOSE run --rm web python manage.py migrate --noinput

log "Coletando estáticos"
$COMPOSE run --rm web python manage.py collectstatic --noinput

log "Recriando serviços da aplicação"
$COMPOSE up -d web celery celery-beat nginx

log "Verificando saúde (tentativas até 12)"
for i in {1..12}; do
  if curl -fsS http://localhost:8000/health/ >/dev/null 2>&1 || curl -fsS http://localhost/health/ >/dev/null 2>&1; then
    ok "Aplicação saudável"
    echo "$IMAGE_TAG" > .last_successful_deploy
    exit 0
  fi
  sleep 5
  warn "Tentativa $i ainda não saudável"
done
err "Aplicação não ficou saudável. Avaliar rollback (scripts/rollback.sh)"
exit 1
