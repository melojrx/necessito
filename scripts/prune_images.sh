#!/usr/bin/env bash
set -euo pipefail
REGISTRY_IMAGE=${REGISTRY_IMAGE:-}
KEEP=${KEEP:-5}
[[ -n $REGISTRY_IMAGE ]] || { echo 'Defina REGISTRY_IMAGE'; exit 1; }
echo "Mantendo últimas $KEEP imagens de $REGISTRY_IMAGE localmente"
IMAGES=$(docker images --format '{{.Repository}}:{{.Tag}} {{.CreatedAt}}' | grep "^$REGISTRY_IMAGE:" | sort -k2 -r | awk '{print $1}')
COUNT=0
for img in $IMAGES; do
  COUNT=$((COUNT+1))
  if [[ $COUNT -le $KEEP ]]; then
    continue
  fi
  echo "Removendo $img"
  docker rmi "$img" || true
done
echo 'Limpeza concluída'
