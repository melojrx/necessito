#!/usr/bin/env bash
set -euo pipefail

# Rollback simplificado (independente de CI/CD)
# Estratégia:
#  - Usa digest/tag passado OU
#  - Usa arquivo last_success_digest (gerado por deploy.sh)
#  - Assume que a imagem já existe localmente ou é pullable

BLUE='\033[0;34m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; RED='\033[0;31m'; NC='\033[0m'
log() { echo -e "${BLUE}[INFO]${NC} $*"; }
ok() { echo -e "${GREEN}[OK]${NC} $*"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $*"; }
err() { echo -e "${RED}[ERR]${NC} $*"; }

COMPOSE_FILE="docker-compose_prod.yml"
COMPOSE="docker compose -f $COMPOSE_FILE"

# Determinar fonte do rollback
REGISTRY_IMAGE=${REGISTRY_IMAGE:-}
IMAGE_DIGEST=${IMAGE_DIGEST:-}
IMAGE_TAG=${IMAGE_TAG:-}

# Se não foi especificado digest ou tag, usar último sucesso conhecido
if [[ -z "$IMAGE_DIGEST" && -z "$IMAGE_TAG" ]]; then
    if [[ -f last_success_digest ]]; then
        IDENTIFIER=$(cat last_success_digest)
        if [[ "$IDENTIFIER" =~ ^sha256: ]]; then
            IMAGE_DIGEST="$IDENTIFIER"
        else
            IMAGE_TAG="$IDENTIFIER"
        fi
    else
        err "Sem digest/tag especificado e sem last_success_digest"; exit 1;
    fi
fi

# Se REGISTRY_IMAGE vazio, inferir do docker-compose (fallback para 'necessito-web')
if [[ -z "$REGISTRY_IMAGE" ]]; then
    REGISTRY_IMAGE=$(grep -E "image:" docker-compose_prod.yml 2>/dev/null | head -1 | awk -F'image:' '{print $2}' | tr -d ' ' | cut -d':' -f1)
    REGISTRY_IMAGE=${REGISTRY_IMAGE:-necessito-web}
    warn "REGISTRY_IMAGE não definido. Usando inferido: ${REGISTRY_IMAGE}"
fi

# Configurar referência da imagem
if [[ -n "$IMAGE_DIGEST" ]]; then
    IMAGE_REF="${REGISTRY_IMAGE}@${IMAGE_DIGEST}"
    IDENTIFIER="$IMAGE_DIGEST"
    DIGEST_SHORT=${IMAGE_DIGEST#sha256:}
    DIGEST_SHORT=${DIGEST_SHORT:0:12}
    export IMAGE_TAG="$DIGEST_SHORT"
else
    IMAGE_REF="${REGISTRY_IMAGE}:${IMAGE_TAG}"
    IDENTIFIER="$IMAGE_TAG"
    export IMAGE_TAG="$IMAGE_TAG"
fi

export REGISTRY_IMAGE="$REGISTRY_IMAGE"

# Log do rollback
mkdir -p logs
TIMESTAMP=$(date -Iseconds)
echo "$TIMESTAMP ROLLBACK_START $IDENTIFIER" >> logs/deploy.log

log "Iniciando rollback para: $IMAGE_REF"

# Pull da imagem de rollback
if [[ "$IMAGE_REF" == *"sha256:"* || -n "$IMAGE_DIGEST" || -n "$IMAGE_TAG" ]]; then
    log "Verificando disponibilidade local da imagem"
    if ! docker image inspect "$IMAGE_REF" >/dev/null 2>&1; then
        log "Imagem não existe localmente – tentando pull: $IMAGE_REF"
        if ! docker pull "$IMAGE_REF"; then
            err "Falha ao obter imagem para rollback: $IMAGE_REF"
            exit 1
        fi
    fi
fi

# Aplicar rollback
log "Aplicando rollback dos serviços"
$COMPOSE up -d web celery celery-beat nginx

# Verificar saúde após rollback
log "Verificando saúde pós-rollback"
sleep 5
HEALTH_URLS=("http://localhost:8000/health/" "https://necessito.online/health/")

for i in {1..10}; do
    for url in "${HEALTH_URLS[@]}"; do
        if curl -fsS --connect-timeout 5 --max-time 10 "$url" >/dev/null 2>&1; then
            ok "Rollback realizado com sucesso!"
            echo "$TIMESTAMP ROLLBACK_OK $IDENTIFIER" >> logs/deploy.log
            exit 0
        fi
    done
    warn "Tentativa $i de health check pós-rollback falhou"; 
    sleep 3
done

err "Rollback aplicado mas health check ainda falha"
echo "$TIMESTAMP ROLLBACK_FAIL $IDENTIFIER" >> logs/deploy.log
exit 1
