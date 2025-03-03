#!/bin/bash

# Configurações
DB_NAME="db.sqlite3"
BACKUP_DIR="backups"
APP_NAME="core"
MIGRATIONS_DIR="$APP_NAME/migrations"
CATEGORIAS_FILE="categorias.txt"
ADMIN_EMAIL="admin@necessito.br"
ADMIN_PASS="il53692007"
ADMIN_FIRST_NAME="Admin"
ADMIN_LAST_NAME="User"

# Gerar nome do backup com timestamp
BACKUP_NAME="${BACKUP_DIR}/db_$(date +%Y%m%d%H%M%S).sqlite3"

echo "🔍 Verificando banco de dados atual..."
mkdir -p "$BACKUP_DIR"

if [ -f "$DB_NAME" ]; then
    cp "$DB_NAME" "$BACKUP_NAME"
    echo "💾 Backup criado em: $BACKUP_NAME"
else
    echo "⚠️ Nenhum banco de dados existente para backup"
fi

echo -e "\n🔄 Reiniciando ambiente de desenvolvimento..."

if [ -f "$DB_NAME" ]; then
    rm "$DB_NAME"
    echo "🗑 Banco de dados removido"
fi

if [ -d "$MIGRATIONS_DIR" ]; then
    rm -rf "$MIGRATIONS_DIR"
    echo "🧹 Migrações antigas removidas"
fi

echo -e "\n🛠 Criando nova estrutura de banco de dados..."
python manage.py makemigrations
python manage.py migrate

if [ -f "$CATEGORIAS_FILE" ]; then
    echo -e "\n📂 Importando categorias..."
    python manage.py import_categorias "$CATEGORIAS_FILE"
else
    echo -e "\n⚠️ Arquivo de categorias não encontrado em: $CATEGORIAS_FILE"
fi

echo -e "\n🛠 Criando superusuário..."
echo "from users.models import User; User.objects.create_superuser(email='$ADMIN_EMAIL', password='$ADMIN_PASS', first_name='$ADMIN_FIRST_NAME', last_name='$ADMIN_LAST_NAME')" | python manage.py shell

echo -e "\n✅ Ambiente reiniciado com sucesso!"
echo "========================================"
echo "👤 Credenciais de acesso:"
echo "   Email: $ADMIN_EMAIL"
echo "   Senha: $ADMIN_PASS"
echo "🔐 Backup disponível em: $BACKUP_NAME"
echo "========================================"