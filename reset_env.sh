#!/bin/bash

# Configurações
DB_NAME="db.sqlite3"
APP_NAME="core"  # Substitua pelo nome do seu app
MIGRATIONS_DIR="$APP_NAME/migrations"
CATEGORIAS_FILE="categorias.txt"  # Ajuste o caminho
ADMIN_USER="admin"
ADMIN_PASS="senha123"  # Altere para uma senha segura

echo "🔄 Reiniciando ambiente de desenvolvimento..."

# Remover banco de dados existente
if [ -f "$DB_NAME" ]; then
    rm "$DB_NAME"
    echo "🗑 Banco de dados removido"
fi

# Remover migrações
if [ -d "$MIGRATIONS_DIR" ]; then
    rm -rf "$MIGRATIONS_DIR"
    echo "🧹 Migrações antigas removidas"
fi

# Criar nova estrutura
python manage.py makemigrations
python manage.py migrate

# Popular categorias
if [ -f "$CATEGORIAS_FILE" ]; then
    python manage.py import_categorias "$CATEGORIAS_FILE"
    echo "📂 Categorias importadas"
else
    echo "⚠️ Arquivo de categorias não encontrado em: $CATEGORIAS_FILE"
fi

# Criar superuser
echo "🛠 Criando superuser..."
python manage.py createsuperuser --noinput --username="$ADMIN_USER" --email="admin@example.com"
echo "from django.contrib.auth.models import User; u = User.objects.get(username='$ADMIN_USER'); u.set_password('$ADMIN_PASS'); u.save()" | python manage.py shell

echo "✅ Ambiente reiniciado com sucesso!"
echo "👤 Acesso admin:"
echo "   Usuário: $ADMIN_USER"
echo "   Senha: $ADMIN_PASS"