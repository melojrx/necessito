#!/bin/bash

# Script de Configuração do Ambiente de Desenvolvimento - Necessito
# Este script configura o ambiente de desenvolvimento completo

set -euo pipefail

echo "🚀 Configurando ambiente de desenvolvimento do Necessito..."

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função para imprimir mensagens coloridas
print_status() { echo -e "${BLUE}[INFO]${NC} $1"; }
print_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
print_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Escolher comando compose (plugin novo preferencialmente)
COMPOSE_CMD="docker compose"
if ! docker compose version >/dev/null 2>&1; then
  if command -v docker-compose >/dev/null 2>&1; then
    print_warning "Plugin 'docker compose' não encontrado. Usando 'docker-compose' legado."
    COMPOSE_CMD="docker-compose"
  else
    print_error "Docker Compose não está instalado (plugin nem legado). Instale o Docker Compose."
    exit 1
  fi
fi

# Verificar se Docker está instalado e rodando
if ! command -v docker >/dev/null 2>&1; then
  print_error "Docker não está instalado. Por favor, instale o Docker primeiro."
  exit 1
fi

if ! docker info >/dev/null 2>&1; then
  print_error "Docker não está em execução. Inicie o serviço do Docker e tente novamente."
  exit 1
fi

print_status "Verificando arquivos de configuração..."

# Verificar se .env.dev existe
if [ ! -f ".env.dev" ]; then
  print_warning "Arquivo .env.dev não encontrado. Criando a partir do .env.example..."
  if [ -f ".env.example" ]; then
    cp .env.example .env.dev
    print_success "Arquivo .env.dev criado com base no .env.example"
  else
    print_error "Arquivo .env.example não encontrado!"
    exit 1
  fi
else
  print_success "Arquivo .env.dev encontrado"
fi

# Parar containers existentes
print_status "Parando containers existentes..."
$COMPOSE_CMD -f docker-compose.dev.yml down --remove-orphans || true

# Construir imagens
print_status "Construindo imagens Docker..."
$COMPOSE_CMD -f docker-compose.dev.yml build --no-cache

# Iniciar serviços de infraestrutura primeiro
print_status "Iniciando serviços de infraestrutura (PostgreSQL e Redis)..."
$COMPOSE_CMD -f docker-compose.dev.yml up -d db redis

# Aguardar PostgreSQL ficar pronto com espera ativa
print_status "Aguardando PostgreSQL ficar pronto..."
MAX_WAIT=60
ELAPSED=0
until $COMPOSE_CMD -f docker-compose.dev.yml exec -T db pg_isready -U "${POSTGRES_USER:-postgres}" -d "${POSTGRES_DB:-necessito_dev}" >/dev/null 2>&1; do
  sleep 2
  ELAPSED=$((ELAPSED+2))
  if [ $ELAPSED -ge $MAX_WAIT ]; then
    print_error "PostgreSQL não ficou pronto após ${MAX_WAIT}s. Verifique os logs."
    $COMPOSE_CMD -f docker-compose.dev.yml logs db | tail -n 100 || true
    exit 1
  fi
  echo -n "."
done
echo
print_success "PostgreSQL está pronto."

# Executar migrações
print_status "Executando migrações do banco de dados..."
$COMPOSE_CMD -f docker-compose.dev.yml run --rm web python manage.py migrate

# Coletar arquivos estáticos
print_status "Coletando arquivos estáticos..."
$COMPOSE_CMD -f docker-compose.dev.yml run --rm web python manage.py collectstatic --noinput

# Criar superusuário (opcional)
read -p "Deseja criar um superusuário? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
  print_status "Criando superusuário..."
  $COMPOSE_CMD -f docker-compose.dev.yml run --rm web python manage.py createsuperuser
fi

# Iniciar todos os serviços
print_status "Iniciando todos os serviços..."
$COMPOSE_CMD -f docker-compose.dev.yml up -d

# Aguardar serviços ficarem prontos (curto)
print_status "Aguardando serviços ficarem prontos..."
sleep 3

# Verificar status dos containers
print_status "Status dos containers:"
$COMPOSE_CMD -f docker-compose.dev.yml ps

print_success "🎉 Ambiente de desenvolvimento configurado com sucesso!"
echo
echo "📋 Informações importantes:"
echo "   • Aplicação: http://localhost (via NGINX)"
echo "   • Django direto: http://localhost:8000 (apenas interno)"
echo "   • Admin: http://localhost/admin"
echo "   • PostgreSQL: localhost:5432"
echo "   • Redis: localhost:6379"
echo "   • NGINX: localhost:80"
echo
echo "📝 Comandos úteis:"
echo "   • Ver logs: $COMPOSE_CMD -f docker-compose.dev.yml logs -f"
echo "   • Parar: $COMPOSE_CMD -f docker-compose.dev.yml down"
echo "   • Reiniciar: $COMPOSE_CMD -f docker-compose.dev.yml restart"
echo "   • Shell Django: $COMPOSE_CMD -f docker-compose.dev.yml exec web python manage.py shell"
echo "   • Bash container: $COMPOSE_CMD -f docker-compose.dev.yml exec web bash"
echo
print_success "Ambiente pronto para desenvolvimento! 🚀"