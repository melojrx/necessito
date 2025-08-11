#!/bin/bash

# Script de Deploy para Produção - Necessito
# Este script realiza o deploy da aplicação em ambiente de produção

echo "🚀 Iniciando deploy em produção do Necessito..."

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função para imprimir mensagens coloridas
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Verificar se está executando como root ou com sudo
if [ "$EUID" -eq 0 ]; then
    print_warning "Executando como root. Certifique-se de que isso é necessário."
fi

# Verificar se Docker está instalado
if ! command -v docker &> /dev/null; then
    print_error "Docker não está instalado. Por favor, instale o Docker primeiro."
    exit 1
fi

# Verificar se Docker Compose está instalado
if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose não está instalado. Por favor, instale o Docker Compose primeiro."
    exit 1
fi

print_status "Verificando arquivos de configuração de produção..."

# Verificar se .env.prod existe
if [ ! -f ".env.prod" ]; then
    print_error "Arquivo .env.prod não encontrado! Crie o arquivo com as configurações de produção."
    exit 1
else
    print_success "Arquivo .env.prod encontrado"
fi

# Verificar se docker-compose_prod.yml existe
if [ ! -f "docker-compose_prod.yml" ]; then
    print_error "Arquivo docker-compose_prod.yml não encontrado!"
    exit 1
else
    print_success "Arquivo docker-compose_prod.yml encontrado"
fi

# Fazer backup dos dados antes do deploy
print_status "Criando backup dos dados..."
mkdir -p backups
DATE=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="backups/backup_${DATE}.sql"

# Tentar fazer backup do banco se estiver rodando
if docker-compose -f docker-compose_prod.yml ps db | grep -q "Up"; then
    print_status "Fazendo backup do banco de dados..."
    docker-compose -f docker-compose_prod.yml exec -T db pg_dump -U postgres necessito_prod > "$BACKUP_FILE"
    if [ $? -eq 0 ]; then
        print_success "Backup criado: $BACKUP_FILE"
    else
        print_warning "Falha ao criar backup do banco"
    fi
else
    print_warning "Banco de dados não está rodando, pulando backup"
fi

# Parar containers existentes
print_status "Parando containers de produção existentes..."
docker-compose -f docker-compose_prod.yml down

# Fazer pull das imagens mais recentes
print_status "Atualizando imagens base..."
docker-compose -f docker-compose_prod.yml pull

# Construir imagens
print_status "Construindo imagens de produção..."
docker-compose -f docker-compose_prod.yml build --no-cache

# Iniciar serviços de infraestrutura primeiro
print_status "Iniciando serviços de infraestrutura..."
docker-compose -f docker-compose_prod.yml up -d db redis

# Aguardar PostgreSQL ficar pronto
print_status "Aguardando PostgreSQL ficar pronto..."
sleep 15

# Executar migrações
print_status "Executando migrações do banco de dados..."
docker-compose -f docker-compose_prod.yml run --rm web python manage.py migrate

# Coletar arquivos estáticos
print_status "Coletando arquivos estáticos..."
docker-compose -f docker-compose_prod.yml run --rm web python manage.py collectstatic --noinput

# Iniciar todos os serviços
print_status "Iniciando todos os serviços de produção..."
docker-compose -f docker-compose_prod.yml up -d

# Aguardar serviços ficarem prontos
print_status "Aguardando serviços ficarem prontos..."
sleep 10

# Verificar status dos containers
print_status "Status dos containers de produção:"
docker-compose -f docker-compose_prod.yml ps

# Verificar se a aplicação está respondendo
print_status "Verificando se a aplicação está respondendo..."
sleep 5
if curl -f http://localhost:8000 > /dev/null 2>&1; then
    print_success "✅ Aplicação está respondendo!"
else
    print_warning "⚠️  Aplicação pode não estar respondendo ainda. Verifique os logs."
fi

# Mostrar logs recentes
print_status "Logs recentes da aplicação:"
docker-compose -f docker-compose_prod.yml logs --tail=20 web

print_success "🎉 Deploy em produção concluído!"
echo
echo "🌐 URLs de Acesso:"
echo "  - HTTPS: https://necessito.online (via nginx-global)"
echo "  - HTTP: http://necessito.online (redirecionado via nginx-global)"
echo "  - Django (interno): necessito-web_prod-1:8000"
echo "  - NGINX Local: nginx-necessito:80"
echo ""
echo "🏗️ Arquitetura VPS Multi-Aplicação:"
echo "  - nginx-global (315aca92d97b) → nginx-necessito:80 → necessito-web_prod-1:8000"
echo "  - SSL/HTTPS gerenciado pelo nginx-global"
echo "  - Rede: nginx-global_global-network + necessito_app_network_prod"
echo ""
echo "📋 Integração com nginx-global:"
echo "  1. Certifique-se que a rede nginx-global_global-network existe"
echo "  2. Configure o proxy no nginx-global para: nginx-necessito:80"
echo "  3. O SSL é gerenciado pelo nginx-global, não localmente"
echo ""
echo "🔧 Comandos Úteis:"
echo "  - Verificar redes: docker network ls"
echo "  - Logs nginx-global: docker logs nginx-global"
echo "  - Logs nginx-necessito: docker logs nginx-necessito"
echo "   • Backup criado: $BACKUP_FILE"
echo
echo "📝 Comandos úteis para produção:"
echo "   • Ver logs: docker-compose -f docker-compose_prod.yml logs -f"
echo "   • Parar: docker-compose -f docker-compose_prod.yml down"
echo "   • Reiniciar: docker-compose -f docker-compose_prod.yml restart"
echo "   • Status: docker-compose -f docker-compose_prod.yml ps"
echo
print_success "Deploy concluído com sucesso! 🚀"