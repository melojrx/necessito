#!/usr/bin/env bash
set -euo pipefail
DB_CONTAINER=${DB_CONTAINER:-db}
FILE=backups/necessito_$(date +%Y%m%d%H%M%S).dump
mkdir -p backups
docker compose -f docker-compose_prod.yml exec -T $DB_CONTAINER pg_dump -U ${POSTGRES_USER:-postgres} -d ${POSTGRES_DB:-necessito_prod} -Fc > "$FILE"
echo "Backup gerado: $FILE"
