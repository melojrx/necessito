# Necessito - Documentação Técnica

## 🛠️ Stack Tecnológica
- Python 3.8+
- Django 4.2+
- Django REST Framework
- PostgreSQL 14+
- Docker & Docker Compose
- Nginx
- Gunicorn
- Bootstrap 5
- JavaScript/TypeScript
  

## ⚙️ Requisitos do Sistema
- Docker 20.10+
- Docker Compose 2.0+
- Git
- Make (opcional, para comandos simplificados)

## 🚀 Inicialização do Ambiente de Desenvolvimento

### Usando Docker Compose (Recomendado)

1. Clone o repositório:
```bash
git clone https://github.com/seu-usuario/necessito.git
cd necessito
```

2. Configure as variáveis de ambiente:
```bash
cp .env.example .env
# Edite o arquivo .env com suas configurações
```

3. Inicie os containers:
```bash
docker-compose up -d
```

4. Execute as migrações:
```bash
docker-compose exec web python manage.py migrate
```

5. Crie um superusuário:
```bash
docker-compose exec web python manage.py createsuperuser
```

### Usando Ambiente Local

1. Crie e ative um ambiente virtual:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

3. Configure o PostgreSQL localmente

4. Execute as migrações:
```bash
python manage.py migrate
```

5. Inicie o servidor de desenvolvimento:
```bash
python manage.py runserver
```

## 📦 Estrutura do Projeto
```
necessito/
├── apps/
│   ├── accounts/          # Autenticação e usuários
│   ├── core/             # Funcionalidades principais
│   ├── marketplace/      # Lógica do marketplace
│   └── services/         # Serviços compartilhados
├── config/               # Configurações do projeto
├── static/              # Arquivos estáticos
├── templates/           # Templates HTML
├── tests/              # Testes automatizados
├── docker/             # Configurações Docker
├── manage.py
├── requirements.txt
└── docker-compose.yml
```

## 🔧 Comandos Úteis

### Docker
```bash
# Iniciar todos os serviços
docker-compose up -d

# Parar todos os serviços
docker-compose down

# Ver logs
docker-compose logs -f

# Executar testes
docker-compose exec web python manage.py test
```

### Django
```bash
# Criar migrações
python manage.py makemigrations

# Aplicar migrações
python manage.py migrate

# Criar superusuário
python manage.py createsuperuser

# Coletar arquivos estáticos
python manage.py collectstatic
```

## 🧪 Testes
```bash
# Executar todos os testes
python manage.py test

# Executar testes específicos
python manage.py test apps.accounts
```

## 📚 Documentação da API
A documentação da API está disponível em:
- Swagger UI: http://localhost:8000/api/docs/
- ReDoc: http://localhost:8000/api/redoc/

## 🔐 Variáveis de Ambiente
Crie um arquivo `.env` na raiz do projeto com as seguintes variáveis:
```env
DEBUG=True
SECRET_KEY=sua-chave-secreta
DATABASE_URL=postgres://user:password@localhost:5432/necessito
REDIS_URL=redis://localhost:6379/0
```

## 🐛 Debugging
- Use `python manage.py shell_plus` para um shell interativo com todos os modelos importados
- Configure o VS Code para debugging com o arquivo `.vscode/launch.json`

## 📝 Convenções de Código
- PEP 8 para Python
- ESLint para JavaScript/TypeScript
- Commits seguindo Conventional Commits
- Branches seguindo Git Flow

## 🔄 CI/CD
O projeto utiliza GitHub Actions para:
- Testes automatizados
- Linting
- Build e deploy
- Análise de segurança

## ⚠️ Troubleshooting
Consulte a pasta `docs/troubleshooting` para soluções de problemas comuns.

## 📧 Suporte Técnico
Para suporte técnico, entre em contato com:
- Email: dev@necessito.br
- Slack: #dev-support 
