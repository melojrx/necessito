#!/usr/bin/env bash
set -euo pipefail

# Script para executar migrações e collectstatic de forma segura
# Usado pelo deploy.sh para garantir integridade da aplicação

BLUE='\033[0;34m'; GREEN='\033[0;32m'; RED='\033[0;31m'; NC='\033[0m'
log() { echo -e "${BLUE}[INFO]${NC} $*"; }
ok() { echo -e "${GREEN}[OK]${NC} $*"; }
err() { echo -e "${RED}[ERR]${NC} $*"; }

COMPOSE_FILE="docker-compose_prod.yml"
COMPOSE="docker compose -f $COMPOSE_FILE"

# Verificar se compose file existe
[[ -f $COMPOSE_FILE ]] || { err "Arquivo $COMPOSE_FILE não encontrado"; exit 1; }

log "Verificando se o banco de dados está acessível"
if ! $COMPOSE exec -T db pg_isready -U necessito_user -d necessito_prod >/dev/null 2>&1; then
    err "Banco de dados não está acessível"
    exit 1
fi

log "Executando Django system check"
if ! $COMPOSE run --rm -e DJANGO_SETTINGS_MODULE=core.settings.prod web python manage.py check --deploy; then
    err "Django system check falhou"
    exit 1
fi

log "Executando migrações do banco de dados"
if ! $COMPOSE run --rm -e DJANGO_SETTINGS_MODULE=core.settings.prod web python manage.py migrate --noinput; then
    err "Migrações falharam"
    exit 1
fi

log "Coletando arquivos estáticos"
if ! $COMPOSE run --rm -e DJANGO_SETTINGS_MODULE=core.settings.prod web python manage.py collectstatic --noinput --clear; then
    err "Collectstatic falhou"
    exit 1
fi

ok "Migrações e collectstatic executados com sucesso"