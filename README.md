# 🏪 Necessito - Marketplace de Necessidades

<div align="center">
  <img src="static/img/logo1.png" alt="Necessito Logo" width="300" />
</div>

[![Django](https://img.shields.io/badge/Django-5.1.4-green.svg)](https://www.djangoproject.com/)
[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://www.python.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-17-blue.svg)](https://www.postgresql.org/)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)
[![CI/CD](https://img.shields.io/badge/CI%2FCD-GitHub%20Actions-green.svg)](https://github.com/features/actions)
[![Production](https://img.shields.io/badge/Production-Active-brightgreen.svg)](https://necessito.online)
[![License](https://img.shields.io/badge/License-Proprietary-red.svg)]()

## 📋 Sobre o Projeto

**Necessito** é uma plataforma marketplace B2B/B2C inovadora que conecta pessoas e empresas com necessidades a fornecedores qualificados. O sistema permite que usuários publiquem suas demandas por produtos ou serviços e recebam orçamentos personalizados de profissionais cadastrados na plataforma.

### 🌐 Produção
- **Website**: [https://necessito.online](https://necessito.online)
- **API**: [https://necessito.online/api/v1/](https://necessito.online/api/v1/)
- **Documentação API**: [https://necessito.online/api/docs/](https://necessito.online/api/docs/)
- **Status**: ✅ **TOTALMENTE FUNCIONAL**

### 🎯 Principais Funcionalidades

- **📢 Publicação de Necessidades**: Usuários podem criar anúncios detalhados de suas necessidades
- **💰 Sistema de Orçamentos**: Fornecedores enviam propostas personalizadas
- **💬 Chat em Tempo Real**: Comunicação direta entre clientes e fornecedores
- **⭐ Avaliações e Reputação**: Sistema de feedback bidirecional
- **🔍 Busca Avançada**: Filtros por categoria, localização e outros critérios
- **📱 API REST**: Integração com aplicativos móveis e externos
- **🔔 Notificações**: Alertas em tempo real sobre novos orçamentos e mensagens
- **📊 Dashboard**: Métricas e estatísticas para usuários

## 🚀 Tecnologias Utilizadas

### Backend
- **Django 5.1.4** - Framework web Python
- **Django REST Framework** - API REST robusta
- **PostgreSQL 17** - Banco de dados relacional principal
- **Redis 7** - Cache e message broker
- **Celery** - Processamento assíncrono e tarefas agendadas
- **WebSocket** - Comunicação em tempo real (chat)
- **Gunicorn** - Servidor WSGI ASGI para produção

### Infraestrutura e DevOps
- **Docker & Docker Compose** - Containerização completa
- **Nginx** - Proxy reverso global com SSL/TLS
- **GitHub Actions** - CI/CD automatizado
- **VPS Ubuntu** - Servidor de produção (31.97.17.10)
- **Let's Encrypt** - Certificados SSL gratuitos
- **Zero Downtime Deployment** - Deploy sem interrupção

### Segurança
- **JWT** - Autenticação de API
- **SSL/TLS** - HTTPS em produção
- **HSTS** - HTTP Strict Transport Security
- **Security Headers** - X-Frame-Options, X-Content-Type-Options
- **Django CORS Headers** - Controle de CORS
- **reCAPTCHA** - Proteção contra bots
- **Firewall UFW** - Proteção de rede

## 📦 Instalação e Configuração

### Pré-requisitos

- Docker e Docker Compose instalados
- Python 3.12+ (para desenvolvimento local sem Docker)
- PostgreSQL 15+ (para desenvolvimento local sem Docker)
- Redis (para desenvolvimento local sem Docker)

### 🐳 Instalação com Docker (Recomendado)

1. **Clone o repositório**
```bash
git clone https://github.com/seu-usuario/indicai.git
cd indicai
```

2. **Configure as variáveis de ambiente**
```bash
cp .env.example .env.dev
# Edite .env.dev com suas configurações
```

3. **Execute o script de configuração**
```bash
chmod +x setup_dev.sh
./setup_dev.sh
```

O script irá:
- Construir as imagens Docker
- Iniciar os containers
- Executar as migrações
- Coletar arquivos estáticos
- Opcionalmente criar um superusuário

4. **Acesse a aplicação**
- Aplicação: http://localhost
- Admin Django: http://localhost/admin
- API: http://localhost/api/v1/
- Documentação API: http://localhost/api/docs/

### 💻 Instalação Local (Sem Docker)

1. **Clone o repositório e crie ambiente virtual**
```bash
git clone https://github.com/seu-usuario/indicai.git
cd indicai
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
```

2. **Instale as dependências**
```bash
pip install -r requirements_dev.txt
```

3. **Configure o banco de dados**
```bash
# Crie um banco PostgreSQL
createdb indicai_dev

# Configure as variáveis de ambiente
cp .env.example .env.dev
# Edite .env.dev com suas configurações de banco
```

4. **Execute as migrações**
```bash
python manage.py migrate
```

5. **Crie um superusuário**
```bash
python manage.py createsuperuser
```

6. **Colete arquivos estáticos**
```bash
python manage.py collectstatic --noinput
```

7. **Inicie o servidor de desenvolvimento**
```bash
python manage.py runserver
```

## 🔧 Comandos Úteis

### Docker
```bash
# Ver logs dos containers
docker-compose -f docker-compose.dev.yml logs -f

# Executar comandos Django no container
docker-compose -f docker-compose.dev.yml exec web python manage.py <comando>

# Acessar shell do container
docker-compose -f docker-compose.dev.yml exec web bash

# Parar todos os containers
docker-compose -f docker-compose.dev.yml down

# Reconstruir imagens
docker-compose -f docker-compose.dev.yml build --no-cache
```

### Django
```bash
# Criar nova migração
python manage.py makemigrations

# Aplicar migrações
python manage.py migrate

# Criar superusuário
python manage.py createsuperuser

# Coletar arquivos estáticos
python manage.py collectstatic

# Shell Django
python manage.py shell

# Executar testes
python manage.py test
```

### Celery
```bash
# Iniciar worker
celery -A core worker -l info

# Iniciar beat (tarefas agendadas)
celery -A core beat -l info
```

## 📁 Estrutura do Projeto

```
indicai/
├── ads/                 # App de anúncios/necessidades
├── api/                 # API REST e serializers
├── budgets/            # Sistema de orçamentos
├── categories/         # Categorias e subcategorias
├── chat/               # Sistema de chat em tempo real
├── core/               # Configurações e utilities centrais
│   └── settings/       # Configurações modulares
├── notifications/      # Sistema de notificações
├── rankings/           # Avaliações e reputação
├── search/             # Funcionalidades de busca
├── users/              # Autenticação e perfis
├── static/             # Arquivos estáticos
├── media/              # Uploads de usuários
├── templates/          # Templates HTML
├── docker-compose.dev.yml
├── docker-compose.prod.yml
├── Dockerfile
├── manage.py
└── requirements_*.txt
```

## 🔑 Variáveis de Ambiente

Principais variáveis que devem ser configuradas no `.env`:

```env
# Django
DJANGO_SECRET_KEY=sua-chave-secreta
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DB_NAME=indicai_dev
DB_USER=postgres
DB_PASSWORD=postgres123
DB_HOST=db
DB_PORT=5432

# Email
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=seu-email@gmail.com
EMAIL_HOST_PASSWORD=sua-senha

# reCAPTCHA
RECAPTCHA_PUBLIC_KEY=sua-chave-publica
RECAPTCHA_PRIVATE_KEY=sua-chave-privada
```

## 📚 API REST

A API REST está disponível em `/api/v1/` com os seguintes endpoints principais:

### Autenticação
- `POST /api/v1/auth/login/` - Login
- `POST /api/v1/auth/logout/` - Logout
- `POST /api/v1/auth/register/` - Registro
- `POST /api/v1/auth/token/refresh/` - Renovar token

### Recursos
- `/api/v1/users/` - Gerenciamento de usuários
- `/api/v1/categories/` - Categorias
- `/api/v1/necessidades/` - Necessidades/Anúncios
- `/api/v1/orcamentos/` - Orçamentos
- `/api/v1/avaliacoes/` - Avaliações

### Documentação
- `/api/docs/` - Documentação interativa OpenAPI/Swagger

## 🧪 Testes

```bash
# Executar todos os testes
python manage.py test

# Executar testes de um app específico
python manage.py test ads
python manage.py test api

# Com coverage
coverage run --source='.' manage.py test
coverage report
```

## 🏗️ Arquitetura de Produção

### Visão Geral da Infraestrutura

O sistema está hospedado em uma VPS Ubuntu que orquestra duas aplicações independentes através de um proxy NGINX global com SSL/TLS:

```
Internet (HTTPS/443 | HTTP/80)
            ↓
    NGINX GLOBAL (SSL/TLS)
    Let's Encrypt Certificates
            ↓
    ┌─────────────────────────┐
    │    NECESSITO APP        │
    │  🛒 Marketplace B2B/B2C  │
    │                         │
    │ nginx-necessito:80      │
    │        ↓                │
    │ necessito-web:8000      │
    │        ↓                │
    │ PostgreSQL 17           │
    │ Redis 7                 │
    │ Celery Workers          │
    └─────────────────────────┘
```

### Containers em Produção

| **Container** | **Função** | **Rede** | **Status** |
|---------------|------------|----------|------------|
| nginx-global | SSL/TLS Proxy | global-network | ✅ Ativo |
| nginx-necessito | App Proxy | necessito + global | ✅ Ativo |
| necessito-web_prod | Django App | necessito | ✅ Ativo |
| necessito-db_prod | PostgreSQL 17 | necessito | ✅ Ativo |
| necessito-redis-prod | Redis 7 | necessito | ✅ Ativo |
| necessito-celery-prod | Celery Worker | necessito | ✅ Ativo |
| necessito-celery-beat-prod | Celery Scheduler | necessito | ✅ Ativo |

### Domínios e SSL

- **Domínios**: necessito.online, www.necessito.online
- **Certificados**: Let's Encrypt (válidos até 18/11/2025)
- **Renovação**: Automática via cron (diariamente às 00:00 e 12:00)
- **Headers**: HSTS, X-Frame-Options, X-Content-Type-Options

## 🚀 CI/CD Pipeline

### GitHub Actions Workflow

O projeto utiliza GitHub Actions para CI/CD automatizado:

```yaml
Trigger: Push to main branch
├── 1. Tests
│   ├── Python 3.12 setup
│   ├── Dependencies install
│   ├── Django tests
│   └── Code quality checks
│
├── 2. Build & Push
│   ├── Docker image build
│   ├── Push to GitHub Container Registry
│   └── Tag with latest/commit hash
│
└── 3. Deploy
    ├── SSH to VPS (31.97.17.10)
    ├── Pull latest image
    ├── Zero downtime deployment
    ├── Database migrations
    ├── Static files collection
    └── Health check validation
```

### Processo de Deploy

1. **Desenvolvimento Local** → `git push origin main`
2. **GitHub Actions** → Testes automáticos
3. **Build & Push** → Docker image para ghcr.io
4. **Deploy Automático** → VPS com zero downtime
5. **Health Check** → Validação de funcionamento

### Scripts de Deploy

| **Script** | **Função** | **Localização** |
|------------|------------|----------------|
| deploy.sh | Deploy principal com zero downtime | /root/necessito/scripts/ |
| migrate.sh | Migrações de banco | /root/necessito/scripts/ |
| collectstatic.sh | Arquivos estáticos | /root/necessito/scripts/ |
| rollback.sh | Rollback para versão anterior | /root/necessito/scripts/ |
| backup_db.sh | Backup do PostgreSQL | /root/necessito/scripts/ |

## 📊 Monitoramento e Backup

### Health Checks
- **Endpoint**: https://necessito.online/health/
- **Monitoramento**: Automático via scripts
- **Logs**: Centralizados em `/root/necessito/logs/`

### Backup Automático
```bash
# Execução diária às 2:00 AM
0 2 * * * /root/necessito/backup_postgres.sh

# Retenção: 7 dias
# Localização: /root/necessito/backups/
# Formato: backup_YYYYMMDD_HHMMSS.sql.gz
```

### Logs e Debugging
```bash
# Logs em tempo real
docker logs necessito-web_prod --tail 100 -f

# Status dos containers
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# Verificar SSL
curl -I https://necessito.online
```


## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📝 Licença

Este projeto é proprietário e confidencial. Todos os direitos reservados.

## 👨‍💻 Desenvolvedor

**Desenvolvido por Júnior Melo**

- **GitHub**: [@melojrx](https://github.com/melojrx)
- **LinkedIn**: [Júnior Melo](https://www.linkedin.com/in/j%C3%BAnior-melo-a4817127/)
- **Email**: suporteindicaai@hotmail.com

### 🛠️ Expertise Técnica

- **Fullstack Development**: Django, React, Node.js
- **DevOps & Infrastructure**: Docker, CI/CD, Linux VPS
- **Database Design**: PostgreSQL, Redis
- **Cloud & Deployment**: GitHub Actions, SSL/TLS, Nginx

## 📞 Suporte e Contato

- **Email**: suporteindicaai@hotmail.com
- **Website**: [https://necessito.online](https://necessito.online)
- **Documentação**: Ver `ARQUITETURA_VPS_INTEGRACAO.md`

## 🎯 Status do Projeto

| **Ambiente** | **Status** | **URL** | **Última Atualização** |
|--------------|------------|---------|----------------------|
| **Produção** | ✅ Ativo | https://necessito.online | 20 de Agosto de 2025 |
| **API** | ✅ Ativo | https://necessito.online/api/v1/ | Versão 1.0 |
| **SSL** | ✅ Válido | Let's Encrypt | Renovação até 18/11/2025 |
| **CI/CD** | ✅ Ativo | GitHub Actions | Deploy automático |

## 📋 Recursos Adicionais

- 📄 **Arquitetura Completa**: `ARQUITETURA_VPS_INTEGRACAO.md`
- 🤖 **Claude AI Guide**: `CLAUDE.md`
- 📊 **Logs de Deploy**: `/root/necessito/logs/`
- 🔄 **Backup Automático**: Diário às 2:00 AM

---

<div align="center">
  
**🏪 Necessito - Marketplace de Necessidades**
  
*Conectando pessoas com necessidades a fornecedores qualificados*

**Desenvolvido com ❤️ por [Júnior Melo](https://github.com/melojrx)**

[![Production](https://img.shields.io/badge/Production-Online-brightgreen.svg)](https://necessito.online)
[![CI/CD](https://img.shields.io/badge/Deploy-Automated-blue.svg)](https://github.com/melojrx/necessito)

</div>