#!/bin/bash

# Aguarda o banco de dados estar pronto
echo "Aguardando banco de dados..."
while ! nc -z db 5432; do
  sleep 0.1
done

echo "Banco de dados conectado!"

# Executa migrações
echo "Executando migrações..."
python manage.py migrate --noinput

# Coleta arquivos estáticos
echo "Coletando arquivos estáticos..."
python manage.py collectstatic --noinput

# Inicia o servidor
echo "Iniciando servidor..."
exec "$@" 