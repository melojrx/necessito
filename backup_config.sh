#!/bin/bash

# ================================================================
# SCRIPT DE BACKUP DAS CONFIGURAÇÕES - NECESSITO
# ================================================================
# Este script faz backup das configurações importantes do projeto

# Criar diretório de backup se não existir
BACKUP_DIR="backups/config"
mkdir -p "$BACKUP_DIR"

# Data atual para nomear os backups
DATE=$(date +"%Y%m%d_%H%M%S")

echo "🔄 Iniciando backup das configurações..."

# Backup do arquivo .env (se existir)
if [ -f ".env" ]; then
    cp .env "$BACKUP_DIR/.env_backup_$DATE"
    echo "✅ Backup do .env criado: $BACKUP_DIR/.env_backup_$DATE"
else
    echo "⚠️  Arquivo .env não encontrado"
fi

# Backup das configurações do Django
if [ -f "core/settings/base.py" ]; then
    cp core/settings/base.py "$BACKUP_DIR/base_py_backup_$DATE"
    echo "✅ Backup do base.py criado: $BACKUP_DIR/base_py_backup_$DATE"
fi

# Backup do docker-compose
if [ -f "docker-compose.override.yml" ]; then
    cp docker-compose.override.yml "$BACKUP_DIR/docker_compose_backup_$DATE"
    echo "✅ Backup do docker-compose.override.yml criado"
fi

# Listar backups existentes
echo ""
echo "📁 Backups disponíveis:"
ls -la "$BACKUP_DIR" | grep backup

echo ""
echo "🎉 Backup concluído com sucesso!"
echo "💡 Para restaurar: cp $BACKUP_DIR/.env_backup_$DATE .env" 