#!/bin/bash

# Script para Pull em Produção - Necessito
# Este script atualiza o código em produção de forma segura

echo "🔄 Iniciando pull em produção do Necessito..."

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

# Verificar se está no diretório correto
if [ ! -f "docker-compose_prod.yml" ]; then
    print_error "Arquivo docker-compose_prod.yml não encontrado! Execute este script no diretório raiz do projeto."
    exit 1
fi

# Verificar se há mudanças não commitadas
if ! git diff-index --quiet HEAD --; then
    print_warning "Há mudanças não commitadas no repositório!"
    echo "Mudanças detectadas:"
    git status --porcelain
    echo
    read -p "Deseja continuar mesmo assim? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_error "Pull cancelado pelo usuário."
        exit 1
    fi
fi

# Mostrar branch atual
CURRENT_BRANCH=$(git branch --show-current)
print_status "Branch atual: $CURRENT_BRANCH"

# Fazer backup do banco antes do pull
print_status "Criando backup de segurança do banco..."
mkdir -p backups
DATE=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="backups/backup_pre_pull_${DATE}.sql"

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

# Fazer pull do código
print_status "Fazendo pull do repositório..."
git pull origin $CURRENT_BRANCH

if [ $? -ne 0 ]; then
    print_error "Falha ao fazer pull do repositório!"
    exit 1
fi

print_success "Pull do código realizado com sucesso"

# Verificar se houve mudanças nos requirements
if git diff HEAD~1 HEAD --name-only | grep -E "requirements.*\.txt$"; then
    print_warning "Detectadas mudanças nos requirements. Será necessário rebuild das imagens."
    REBUILD_NEEDED=true
else
    REBUILD_NEEDED=false
fi

# Verificar se houve mudanças no Dockerfile
if git diff HEAD~1 HEAD --name-only | grep -E "Dockerfile$"; then
    print_warning "Detectadas mudanças no Dockerfile. Será necessário rebuild das imagens."
    REBUILD_NEEDED=true
fi

# Verificar se houve mudanças nas migrações
MIGRATIONS_CHANGED=false
if git diff HEAD~1 HEAD --name-only | grep -E "migrations/.*\.py$"; then
    print_warning "Detectadas novas migrações do banco de dados."
    MIGRATIONS_CHANGED=true
fi

# Rebuild se necessário
if [ "$REBUILD_NEEDED" = true ]; then
    print_status "Reconstruindo imagens devido a mudanças nos requirements ou Dockerfile..."
    docker-compose -f docker-compose_prod.yml build --no-cache web
    
    if [ $? -ne 0 ]; then
        print_error "Falha ao reconstruir as imagens!"
        exit 1
    fi
    
    print_success "Imagens reconstruídas com sucesso"
fi

# Executar migrações se necessário
if [ "$MIGRATIONS_CHANGED" = true ]; then
    print_status "Executando novas migrações do banco de dados..."
    docker-compose -f docker-compose_prod.yml run --rm web python manage.py migrate
    
    if [ $? -ne 0 ]; then
        print_error "Falha ao executar migrações!"
        print_error "Considere restaurar o backup: $BACKUP_FILE"
        exit 1
    fi
    
    print_success "Migrações executadas com sucesso"
fi

# Coletar arquivos estáticos
print_status "Coletando arquivos estáticos..."
docker-compose -f docker-compose_prod.yml run --rm web python manage.py collectstatic --noinput

if [ $? -ne 0 ]; then
    print_warning "Falha ao coletar arquivos estáticos"
fi

# Reiniciar serviços da aplicação (sem afetar banco e redis)
print_status "Reiniciando serviços da aplicação..."
docker-compose -f docker-compose_prod.yml restart web celery celery-beat nginx

if [ $? -ne 0 ]; then
    print_error "Falha ao reiniciar serviços!"
    exit 1
fi

# Aguardar serviços ficarem prontos
print_status "Aguardando serviços ficarem prontos..."
sleep 10

# Verificar status dos containers
print_status "Status dos containers após o pull:"
docker-compose -f docker-compose_prod.yml ps

# Verificar se a aplicação está respondendo
print_status "Verificando se a aplicação está respondendo..."
sleep 5
if curl -f http://localhost:8000/health/ > /dev/null 2>&1; then
    print_success "✅ Aplicação está respondendo!"
else
    print_warning "⚠️  Aplicação pode não estar respondendo ainda. Verifique os logs."
    echo "Logs recentes:"
    docker-compose -f docker-compose_prod.yml logs --tail=10 web
fi

print_success "🎉 Pull em produção concluído com sucesso!"
echo
echo "📋 Resumo das ações realizadas:"
echo "  ✅ Backup do banco criado: $BACKUP_FILE"
echo "  ✅ Pull do código realizado"
if [ "$REBUILD_NEEDED" = true ]; then
    echo "  ✅ Imagens reconstruídas"
fi
if [ "$MIGRATIONS_CHANGED" = true ]; then
    echo "  ✅ Migrações executadas"
fi
echo "  ✅ Arquivos estáticos coletados"
echo "  ✅ Serviços reiniciados"
echo
echo "🔧 Comandos úteis pós-pull:"
echo "  • Ver logs: docker-compose -f docker-compose_prod.yml logs -f web"
echo "  • Status: docker-compose -f docker-compose_prod.yml ps"
echo "  • Rollback (se necessário): git reset --hard HEAD~1"
echo "  • Restaurar backup: docker-compose -f docker-compose_prod.yml exec -T db psql -U postgres necessito_prod < $BACKUP_FILE"
echo
print_success "Pull concluído! 🚀"