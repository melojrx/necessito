# 🏪 Indicaai - Marketplace de Necessidades

<div align="center">
  <img src="static/img/logo1.png" alt="Indicai Logo" width="300" />
</div>

[![Django](https://img.shields.io/badge/Django-5.1.10-green.svg)](https://www.djangoproject.com/)
[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://www.python.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-blue.svg)](https://www.postgresql.org/)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)
[![License](https://img.shields.io/badge/License-Proprietary-red.svg)]()

## 📋 Sobre o Projeto

**Indicaai** é uma plataforma marketplace inovadora que conecta pessoas com necessidades a fornecedores qualificados. O sistema permite que usuários publiquem suas demandas por produtos ou serviços e recebam orçamentos de profissionais cadastrados na plataforma.

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
- **Django 5.1.10** - Framework web Python
- **Django REST Framework** - API REST robusta
- **PostgreSQL** - Banco de dados relacional
- **Redis** - Cache e message broker
- **Celery** - Processamento assíncrono
- **WebSocket** - Comunicação em tempo real

### Infraestrutura
- **Docker & Docker Compose** - Containerização
- **Nginx** - Servidor web e proxy reverso
- **Gunicorn** - Servidor WSGI para produção

### Segurança
- **JWT** - Autenticação de API
- **Django CORS Headers** - Controle de CORS
- **reCAPTCHA** - Proteção contra bots

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

## 🚢 Deploy em Produção

### Com Docker

1. Configure as variáveis de ambiente de produção:
```bash
cp .env.example .env.prod
# Configure com valores de produção
```

2. Execute o deploy:
```bash
./deploy_prod.sh
```

### Configurações de Segurança

Em produção, certifique-se de:
- Definir `DEBUG=False`
- Configurar `ALLOWED_HOSTS` corretamente
- Usar HTTPS (SSL/TLS)
- Configurar um servidor de email real
- Usar senhas fortes para banco de dados
- Configurar backups automáticos

## 📈 Monitoramento

O sistema inclui:
- Logs estruturados em `/logs/`
- Métricas de performance
- Monitoramento de tarefas Celery
- Alertas de erro via email

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📝 Licença

Este projeto é proprietário e confidencial. Todos os direitos reservados.

## 📞 Contato

- Email: suporteindicaai@hotmail.com
- Website: [https://necessito.online/](https://necessito.online/)

## 🙏 Agradecimentos

- Equipe de desenvolvimento
- Comunidade Django
- Todos os contribuidores do projeto

---

**Desenvolvido com ❤️ pela equipe Indicai**