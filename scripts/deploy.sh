#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'

# Deploy com tracking por digest - MVP Pipeline v2.0
# Pressupõe:
#  - docker compose plugin instalado
#  - arquivo docker-compose_prod.yml no diretório raiz
#  - .env.prod presente (não versionado)
#  - Suporte para digest (REGISTRY_IMAGE@sha256:...) ou tag

BLUE='\033[0;34m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; RED='\033[0;31m'; NC='\033[0m'
log(){ echo -e "${BLUE}[INFO]${NC} $*"; }
ok(){ echo -e "${GREEN}[OK]${NC} $*"; }
warn(){ echo -e "${YELLOW}[WARN]${NC} $*"; }
err(){ echo -e "${RED}[ERR]${NC} $*"; }

COMPOSE_FILE="docker-compose_prod.yml"
COMPOSE="docker compose -f $COMPOSE_FILE"

[[ -f $COMPOSE_FILE ]] || { err "Arquivo $COMPOSE_FILE não encontrado"; exit 1; }
[[ -f .env.prod ]] || { err "Arquivo .env.prod não encontrado"; exit 1; }

# Suporte para digest (preferido) ou tag tradicional
REGISTRY_IMAGE=${REGISTRY_IMAGE:-}
IMAGE_DIGEST=${IMAGE_DIGEST:-}
IMAGE_TAG=${IMAGE_TAG:-}

# Priorizar digest sobre tag
if [[ -n "$IMAGE_DIGEST" ]]; then
  IMAGE_REF="${REGISTRY_IMAGE}@${IMAGE_DIGEST}"
  IDENTIFIER="$IMAGE_DIGEST"
elif [[ -n "$IMAGE_TAG" ]]; then
  IMAGE_REF="${REGISTRY_IMAGE}:${IMAGE_TAG}" 
  IDENTIFIER="$IMAGE_TAG"
else
  err "Defina IMAGE_DIGEST (preferido) ou IMAGE_TAG"; exit 1;
fi

[[ -n "$REGISTRY_IMAGE" ]] || { err "Defina REGISTRY_IMAGE"; exit 1; }

# Criar diretório de logs se não existir
mkdir -p logs

# Log de auditoria com timestamp ISO 8601
LOG_FILE="logs/deploy.log"
TIMESTAMP=$(date -Iseconds)
DIGEST_SHORT=""
if [[ -n "$IMAGE_DIGEST" ]]; then
  DIGEST_SHORT=${IMAGE_DIGEST#sha256:}
  DIGEST_SHORT=${DIGEST_SHORT:0:12}
fi

echo "$TIMESTAMP START ${IDENTIFIER}" | tee -a "$LOG_FILE"
log "Iniciando deploy: ${IMAGE_REF}"
log "Identificador: ${IDENTIFIER}"

# Verificar se já está em produção
CURRENT_IMAGE="$(docker ps --format '{{.Names}} {{.Image}}' | awk '/necessito-web_prod/ {print $2}')" || CURRENT_IMAGE=""
log "Imagem atualmente em produção: ${CURRENT_IMAGE:-<nenhuma>}"

if [[ "${IMAGE_REF}" == "${CURRENT_IMAGE}" ]]; then
  warn "A imagem ${IMAGE_REF} já está em produção. Prosseguindo mesmo assim."
fi

log "Pull da imagem: ${IMAGE_REF}"
docker pull "${IMAGE_REF}"

# Configurar variáveis para docker-compose (usando tag para compatibilidade)
if [[ -n "$IMAGE_DIGEST" ]]; then
  # Para digest, usar o short hash como tag
  export IMAGE_TAG="$DIGEST_SHORT"
else
  export IMAGE_TAG="${IMAGE_TAG}"
fi
export REGISTRY_IMAGE="${REGISTRY_IMAGE}"

log "Subindo dependências (db, redis) se ainda não estiverem ativas"
$COMPOSE up -d db redis

# Executar migrate e collectstatic usando script dedicado
log "Executando migrações e collectstatic"
if ./scripts/migrate_collectstatic.sh; then
  ok "Migrações e estáticos aplicados com sucesso"
else
  err "Falha nas migrações/estáticos"
  echo "$TIMESTAMP FAIL ${IDENTIFIER} - migrations" | tee -a "$LOG_FILE"
  exit 1
fi

log "Recriando serviços da aplicação com zero downtime"
$COMPOSE up -d web
sleep 3
$COMPOSE up -d celery celery-beat nginx

log "Verificando saúde da aplicação (até 15 tentativas)"
HEALTH_URLS=("http://localhost:8000/health/" "https://necessito.online/health/")
HEALTH_OK=false

for i in {1..15}; do
  for url in "${HEALTH_URLS[@]}"; do
    if curl -fsS --connect-timeout 5 --max-time 10 "$url" >/dev/null 2>&1; then
      ok "Health check OK em $url"
      HEALTH_OK=true
      break 2
    fi
  done
  warn "Tentativa $i falhou, aguardando..."; 
  sleep 4
done

if [[ "$HEALTH_OK" == "true" ]]; then
  # Sucesso - registrar digest/tag para rollback futuro
  echo "$IDENTIFIER" > last_success_digest
  echo "${IMAGE_REF}" > .last_successful_image
  echo "$TIMESTAMP OK ${IDENTIFIER}" | tee -a "$LOG_FILE"
  ok "Deploy realizado com sucesso! Imagem: ${IMAGE_REF}"
  exit 0
else
  # Falha - iniciar rollback automático
  err "Health check falhou após todas as tentativas"
  echo "$TIMESTAMP FAIL ${IDENTIFIER} - health_check" | tee -a "$LOG_FILE"
  
  if [[ -f last_success_digest ]]; then
    PREV_DIGEST=$(cat last_success_digest)
    warn "Iniciando rollback automático para: $PREV_DIGEST"
    echo "$TIMESTAMP ROLLBACK ${IDENTIFIER} -> ${PREV_DIGEST}" | tee -a "$LOG_FILE"
    
    # Configurar variáveis para rollback
    if [[ "$PREV_DIGEST" =~ ^sha256: ]]; then
      REGISTRY_IMAGE="$REGISTRY_IMAGE" IMAGE_DIGEST="$PREV_DIGEST" ./scripts/rollback.sh
    else
      REGISTRY_IMAGE="$REGISTRY_IMAGE" IMAGE_TAG="$PREV_DIGEST" ./scripts/rollback.sh
    fi
  else
    err "Sem versão anterior para rollback disponível"
  fi
  exit 1
fi
