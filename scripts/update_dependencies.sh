#!/bin/bash

# Script para atualizar dependências e corrigir vulnerabilidades

echo "==================================="
echo "Atualizando dependências de segurança"
echo "==================================="

# Ativar ambiente virtual se existir
if [ -d "venv" ]; then
    source venv/bin/activate
elif [ -d ".venv" ]; then
    source .venv/bin/activate
elif [ -d "env" ]; then
    source env/bin/activate
fi

# Atualizar pip
echo "Atualizando pip..."
pip install --upgrade pip

# Instalar/atualizar pacotes com vulnerabilidades corrigidas
echo "Instalando dependências atualizadas..."
pip install --upgrade \
    Django==5.1.10 \
    djangorestframework==3.15.2 \
    djangorestframework-simplejwt==5.3.2 \
    requests==2.32.4 \
    urllib3==2.5.0 \
    PyJWT==2.10.1

echo "==================================="
echo "Verificando instalação..."
echo "==================================="

python3 -c "
import django
import rest_framework
import requests
import urllib3

print(f'Django: {django.__version__}')
print(f'DRF: {rest_framework.__version__}')
print(f'Requests: {requests.__version__}')
print(f'Urllib3: {urllib3.__version__}')
"

echo "==================================="
echo "Dependências atualizadas com sucesso!"
echo "====================================="