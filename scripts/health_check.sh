#!/usr/bin/env bash
set -euo pipefail
# Script reutilizável para checar saúde da aplicação Necessito.
# Uso: ./scripts/health_check.sh [tentativas] [intervalo_segundos]
ATTEMPTS=${1:-5}
INTERVAL=${2:-3}
URLS=("http://localhost:8000/health/" "http://localhost/health/" "https://necessito.online/health/")
for i in $(seq 1 "$ATTEMPTS"); do
  for u in "${URLS[@]}"; do
    if curl -fsS "$u" >/dev/null 2>&1; then
      echo "OK $u"; exit 0; fi
  done
  sleep "$INTERVAL"
done
echo "FALHA: nenhuma URL respondeu com sucesso" >&2
exit 1