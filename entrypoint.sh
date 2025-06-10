#!/bin/bash

# Coleta arquivos estáticos
echo "Coletando arquivos estáticos..."
python manage.py collectstatic --noinput

# Inicia o servidor
echo "Iniciando servidor..."
exec "$@" 