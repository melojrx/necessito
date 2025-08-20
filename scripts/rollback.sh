#!/usr/bin/env bash
set -euo pipefail

BLUE='\033[0;34m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; RED='\033[0;31m'; NC='\033[0m'
log(){ echo -e "${BLUE}[INFO]${NC} $*"; }
ok(){ echo -e "${GREEN}[OK]${NC} $*"; }
err(){ echo -e "${RED}[ERR]${NC} $*"; }

[[ -f .last_successful_deploy ]] || { err "Sem registro de deploy anterior (.last_successful_deploy)"; exit 1; }
TAG=$(cat .last_successful_deploy)
REGISTRY_IMAGE=${REGISTRY_IMAGE:-}
[[ -n "$REGISTRY_IMAGE" ]] || { err "Defina REGISTRY_IMAGE"; exit 1; }

log "Rollback para tag $TAG"
sed -i.bak -e "s|image: ${REGISTRY_IMAGE}:.*|image: ${REGISTRY_IMAGE}:${TAG}|" docker-compose_prod.yml
docker compose pull web || true
docker compose up -d web celery celery-beat nginx
ok "Rollback aplicado"
