#!/usr/bin/env bash
set -euo pipefail
[[ -f docker-compose_prod.yml ]] || { echo 'docker-compose_prod.yml não encontrado'; exit 1; }
docker compose run --rm web python manage.py collectstatic --noinput
echo 'Arquivos estáticos coletados'
