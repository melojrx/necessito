# Guia de Deploy Manual Simplificado

Estado atual: CI/CD removido. Deploy realizado manualmente via VPS usando Docker Compose + scripts.

## 1. Opções de Deploy

1. Build local e subir (sem registry)
2. Usar imagem de um registry (fornecer REGISTRY_IMAGE + IMAGE_TAG ou IMAGE_DIGEST)

## 2. Primeira Preparação (VPS)

```bash
apt update && apt install -y git docker.io docker-compose-plugin
git clone https://github.com/SEU_USER/necessito.git /opt/necessito
cd /opt/necessito
cp .env.prod.example .env.prod
nano .env.prod   # ajustar variáveis
chmod +x scripts/*.sh
```

## 3. Deploy - Build Local

```bash
cd /opt/necessito
./scripts/deploy.sh
```
O script fará: build -> migrações -> collectstatic -> subir serviços -> health check.

## 4. Deploy - Usando Imagem do Registry

```bash
export REGISTRY_IMAGE=ghcr.io/SEU_USER/necessito-web
export IMAGE_TAG=latest   # ou defina IMAGE_DIGEST=sha256:...
./scripts/deploy.sh
```

## 5. Rollback

Automático: se health falhar, script tenta voltar à última versão registrada em `last_success_digest`.

Manual:
```bash
cd /opt/necessito
./scripts/rollback.sh                 # usa last_success_digest
REGISTRY_IMAGE=necessito-web IMAGE_TAG=manual-202501011230 ./scripts/rollback.sh
```

## 6. Estruturas de Estado

| Arquivo | Função |
|---------|--------|
| logs/deploy.log | Histórico com timestamps |
| last_success_digest | Último identificador bem sucedido (tag curta ou digest) |
| .last_successful_image | Referência completa (image[:tag] ou image@digest) |

## 7. Health Check

URLs verificadas: `http://localhost:8000/health/` e `https://necessito.online/health/`.
Ajuste no script se domínio mudar.

## 8. Atualização de Código

Sem pipeline, atualize manualmente:
```bash
cd /opt/necessito
git pull origin main
./scripts/deploy.sh    # rebuild ou pull conforme variáveis
```

## 9. Rotina de Manutenção

- Backups: garantir cron/backup_db.sh (adaptar se necessário)
- Limpeza de imagens antigas:
  ```bash
  docker image prune -f
  ```
- Verificar disco / logs / certificados SSL (global nginx).

## 10. Boas Práticas Sem CI

- Testar local antes de cada deploy.
- Commits pequenos e mensuráveis.
- Registrar manualmente mudanças relevantes (CHANGELOG ou log de deploy).

## 11. Quando Reconsiderar CI/CD

Reintroduzir pipeline quando:
- Precisar de verificação automática de testes.
- Aumentar número de contribuidores.
- Necessidade de métricas de qualidade e segurança.

---
Documento focado no fluxo operacional mínimo. Qualquer vestígio de GitHub Actions nos outros docs pode ser limpo gradualmente.