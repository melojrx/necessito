# ============================================================================
# NECESSITO - Makefile para Desenvolvimento
# ============================================================================
# Comandos convenientes para gerenciar o ambiente de desenvolvimento Docker
#
# Uso: make <comando>
# Exemplo: make dev
# ============================================================================

.PHONY: help dev stop restart logs build migrate makemigrations shell createsuperuser test clean celery collectstatic psql redis-cli

# Arquivo do Docker Compose
COMPOSE_FILE := docker-compose_dev.yml
COMPOSE := docker compose -f $(COMPOSE_FILE)

# Service names (use in compose exec commands)
WEB_SERVICE := web
DB_SERVICE := db
REDIS_SERVICE := redis

# ============================================================================
# COMANDOS PRINCIPAIS
# ============================================================================

## help: Mostra esta mensagem de ajuda
help:
	@echo "╔════════════════════════════════════════════════════════════════╗"
	@echo "║         NECESSITO - Comandos de Desenvolvimento               ║"
	@echo "╚════════════════════════════════════════════════════════════════╝"
	@echo ""
	@echo "🚀 Comandos Principais:"
	@echo "  make dev              - Iniciar ambiente de desenvolvimento"
	@echo "  make stop             - Parar todos os containers"
	@echo "  make restart          - Reiniciar todos os containers"
	@echo "  make logs             - Ver logs em tempo real"
	@echo "  make build            - Rebuild das imagens Docker"
	@echo ""
	@echo "🗄️  Banco de Dados:"
	@echo "  make migrate          - Executar migrations"
	@echo "  make makemigrations   - Criar novas migrations"
	@echo "  make psql             - Acessar PostgreSQL via psql"
	@echo ""
	@echo "👨‍💻 Django:"
	@echo "  make shell            - Django shell interativo"
	@echo "  make createsuperuser  - Criar superusuário"
	@echo "  make collectstatic    - Coletar arquivos estáticos"
	@echo "  make test             - Executar testes"
	@echo ""
	@echo "⚡ Celery:"
	@echo "  make celery           - Iniciar com Celery worker"
	@echo ""
	@echo "🧹 Limpeza:"
	@echo "  make clean            - Remover containers, volumes e networks"
	@echo "  make redis-cli        - Acessar Redis CLI"
	@echo ""
	@echo "Para mais informações: cat CLAUDE.md"
	@echo ""

## dev: Inicia o ambiente de desenvolvimento
dev:
	@echo "🚀 Iniciando ambiente de desenvolvimento..."
	$(COMPOSE) up -d
	@echo "✅ Ambiente iniciado com sucesso!"
	@echo ""
	@echo "🌐 Acesse: http://localhost:8000"
	@echo "🔧 Admin: http://localhost:8000/admin"
	@echo "📚 API Docs: http://localhost:8000/api/docs"
	@echo ""
	@echo "💡 Para ver logs: make logs"

## stop: Para todos os containers
stop:
	@echo "🛑 Parando containers..."
	$(COMPOSE) down
	@echo "✅ Containers parados!"

## restart: Reinicia todos os containers
restart: stop dev

## logs: Mostra logs em tempo real
logs:
	$(COMPOSE) logs -f

## build: Rebuild das imagens Docker
build:
	@echo "🔨 Rebuilding imagens Docker..."
	$(COMPOSE) build --no-cache
	@echo "✅ Imagens rebuilded!"

# ============================================================================
# BANCO DE DADOS
# ============================================================================

## migrate: Executa migrations do Django
migrate:
	@echo "🗄️  Executando migrations..."
	$(COMPOSE) exec $(WEB_SERVICE) python manage.py migrate
	@echo "✅ Migrations executadas!"

## makemigrations: Cria novas migrations
makemigrations:
	@echo "📝 Criando migrations..."
	$(COMPOSE) exec $(WEB_SERVICE) python manage.py makemigrations
	@echo "✅ Migrations criadas!"

## psql: Acessa o PostgreSQL via psql
psql:
	@echo "🗄️  Acessando PostgreSQL..."
	$(COMPOSE) exec $(DB_SERVICE) psql -U postgres -d necessito_dev

# ============================================================================
# DJANGO
# ============================================================================

## shell: Abre o Django shell
shell:
	@echo "🐍 Abrindo Django shell..."
	$(COMPOSE) exec $(WEB_SERVICE) python manage.py shell

## createsuperuser: Cria um superusuário
createsuperuser:
	@echo "👤 Criando superusuário..."
	$(COMPOSE) exec $(WEB_SERVICE) python manage.py createsuperuser

## collectstatic: Coleta arquivos estáticos
collectstatic:
	@echo "📦 Coletando arquivos estáticos..."
	$(COMPOSE) exec $(WEB_SERVICE) python manage.py collectstatic --noinput
	@echo "✅ Arquivos estáticos coletados!"

## test: Executa os testes
test:
	@echo "🧪 Executando testes..."
	$(COMPOSE) exec $(WEB_SERVICE) python manage.py test

# ============================================================================
# CELERY
# ============================================================================

## celery: Inicia o ambiente com Celery worker
celery:
	@echo "⚡ Iniciando com Celery worker..."
	$(COMPOSE) --profile celery up -d
	@echo "✅ Celery worker iniciado!"
	@echo "💡 Para ver logs: make logs"

# ============================================================================
# LIMPEZA E MANUTENÇÃO
# ============================================================================

## clean: Remove containers, volumes e networks
clean:
	@echo "🧹 Removendo containers, volumes e networks..."
	$(COMPOSE) down -v --remove-orphans
	@echo "✅ Limpeza concluída!"

## redis-cli: Acessa o Redis CLI
redis-cli:
	@echo "📦 Acessando Redis CLI..."
	$(COMPOSE) exec $(REDIS_SERVICE) redis-cli

# ============================================================================
# COMANDOS AVANÇADOS
# ============================================================================

## status: Mostra o status dos containers
status:
	@echo "📊 Status dos containers:"
	@docker ps --filter "name=necessito" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

## exec-web: Abre bash no container web
exec-web:
	@echo "🐚 Abrindo bash no container web..."
	$(COMPOSE) exec $(WEB_SERVICE) bash

## exec-db: Abre bash no container db
exec-db:
	@echo "🐚 Abrindo bash no container db..."
	$(COMPOSE) exec $(DB_SERVICE) bash

# Default target
.DEFAULT_GOAL := help
