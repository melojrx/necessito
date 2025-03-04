#!/bin/bash

# Configurações do Windows
DB_NAME="db.sqlite3"
BACKUP_DIR="backups"
APP_NAME="core"
MIGRATIONS_DIR="$APP_NAME/migrations"
CATEGORIAS_FILE="categorias.txt"
ADMIN_EMAIL="admin@necessito.br"
ADMIN_PASS="il53692007"
ADMIN_FIRST_NAME="Admin"
ADMIN_LAST_NAME="User"

# Configurar timestamp para backup
BACKUP_NAME="${BACKUP_DIR}/db_$(date +%Y%m%d%H%M%S).sqlite3"

echo "🔍 Verificando banco de dados atual..."
mkdir -p "$BACKUP_DIR"

# Fazer backup se o banco existir
if [ -f "$DB_NAME" ]; then
    cp "$DB_NAME" "$BACKUP_NAME"
    echo "💾 Backup criado em: $BACKUP_NAME"
else
    echo "⚠️ Nenhum banco de dados existente para backup"
fi

echo -e "\n🔄 Reiniciando ambiente de desenvolvimento..."

# Remover arquivos existentes
if [ -f "$DB_NAME" ]; then
    rm -f "$DB_NAME"
    echo "🗑 Banco de dados removido"
fi

if [ -d "$MIGRATIONS_DIR" ]; then
    rm -rf "$MIGRATIONS_DIR"
    echo "🧹 Migrações antigas removidas"
fi

echo -e "\n🛠 Criando nova estrutura de banco de dados..."
python manage.py makemigrations --noinput
python manage.py migrate --noinput

# Processar categorias
if [ -f "$CATEGORIAS_FILE" ]; then
    echo -e "\n📂 Processando categorias..."
    
    # Criar versão limpa do arquivo
    CLEANED_FILE="${CATEGORIAS_FILE}.clean"
    grep -vE '^[0-9]+\. ' "$CATEGORIAS_FILE" | sed 's/^ *//;s/ *$//' > "$CLEANED_FILE"
    
    # Converter caminho para formato Windows
    WIN_FILE=$(cygpath -w "$CLEANED_FILE")
    
    echo "⌛ Importando categorias de: $WIN_FILE"
    python manage.py import_categorias "$WIN_FILE"
    rm "$CLEANED_FILE"
else
    echo -e "\n⚠️ Arquivo de categorias não encontrado em: $CATEGORIAS_FILE"
fi

echo -e "\n🛠 Criando superusuário..."
# Criar usuário sem senha
python manage.py createsuperuser \
    --email "$ADMIN_EMAIL" \
    --first_name "$ADMIN_FIRST_NAME" \
    --last_name "$ADMIN_LAST_NAME" \
    --noinput

# Definir senha
echo "from django.contrib.auth import get_user_model; User = get_user_model(); user = User.objects.get(email='$ADMIN_EMAIL'); user.set_password('$ADMIN_PASS'); user.save()" | python manage.py shell

echo -e "\n✅ Ambiente reiniciado com sucesso!"
echo "========================================"
echo "👤 Credenciais de acesso:"
echo "   Email: $ADMIN_EMAIL"
echo "   Senha: $ADMIN_PASS"
echo "🔐 Backup disponível em: $BACKUP_NAME"
echo "========================================"