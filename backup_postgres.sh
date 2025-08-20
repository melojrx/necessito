#!/usr/bin/env bash
set -euo pipefail

# Script de backup do PostgreSQL para Necessito
# Executa backup do banco de dados em produção

# Diretório de backup
BACKUP_DIR="/root/necessito/backups"
mkdir -p "$BACKUP_DIR"

# Carregar variáveis de ambiente
if [ -f /root/necessito/.env.prod ]; then
    export $(grep -v '^#' /root/necessito/.env.prod | xargs)
fi

# Nome do arquivo de backup com timestamp
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/necessito_prod_${TIMESTAMP}.sql"

# Executar backup usando docker compose
cd /root/necessito
docker compose -f docker-compose_prod.yml exec -T db pg_dump -U ${POSTGRES_USER:-necessito_user} ${POSTGRES_DB:-necessito_prod} > "$BACKUP_FILE"

# Comprimir o backup
gzip "$BACKUP_FILE"

# Manter apenas os últimos 7 dias de backups
find "$BACKUP_DIR" -name "necessito_prod_*.sql.gz" -mtime +7 -delete

echo "Backup concluído: ${BACKUP_FILE}.gz"