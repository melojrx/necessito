# Indicaai - Marketplace

<div align="center">
  <img src="static/img/logo1.png" alt="Indicaai Logo" width="300"/>
  <br/>
  <h3>Conectando necessidades às melhores soluções</h3>
</div>

---

## 📋 Sobre o Projeto

O **Indicaai** é uma plataforma marketplace inovadora que conecta pessoas e empresas que têm necessidades específicas com fornecedores qualificados. Nossa solução facilita o processo de encontrar, negociar e contratar serviços e produtos de forma eficiente e segura.

## 🎯 Nossa Missão

Transformar a maneira como necessidades são atendidas, criando um ecossistema digital confiável que beneficia tanto quem precisa quanto quem oferece soluções, através de tecnologia de ponta e experiência de usuário excepcional.

## ✨ Funcionalidades Principais

### 🎯 **Sistema de Anúncios**
- Publicação de necessidades com descrição detalhada
- Upload de múltiplas imagens
- Categorização inteligente
- Geolocalização automática

### 💰 **Sistema de Orçamentos**
- Recebimento de propostas personalizadas
- Geração automática de PDFs
- Controle de status e negociação
- Histórico completo de orçamentos

### 💬 **Comunicação Integrada**
- Chat em tempo real entre usuários
- Notificações instantâneas
- Histórico de conversas
- Sistema de mensagens contextual

### ⭐ **Sistema de Avaliações**
- Avaliação bidirecional entre usuários
- Sistema de reputação confiável
- Comentários detalhados
- Ranking de fornecedores

### 🔍 **Busca Avançada**
- Filtros por localização, categoria e preço
- Busca inteligente com algoritmos otimizados
- Sugestões personalizadas
- Resultados georreferenciados

### 👥 **Gestão de Usuários**
- Perfis completos e verificados
- Geolocalização automática
- Sistema de autenticação seguro
- Painel administrativo completo

## 🛠️ Tecnologias Utilizadas

### **Backend**
- **Python 3.8+** - Linguagem principal
- **Django 4.2+** - Framework web robusto
- **Django REST Framework** - API REST completa
- **PostgreSQL** - Banco de dados relacional
- **Celery** - Processamento assíncrono

### **Frontend**
- **HTML5/CSS3** - Estrutura e estilização
- **JavaScript ES6+** - Interatividade
- **Bootstrap 5** - Framework CSS responsivo
- **AJAX** - Requisições assíncronas

### **Infraestrutura**
- **Docker** - Containerização
- **Nginx** - Servidor web e proxy reverso
- **Let's Encrypt** - Certificados SSL
- **AWS S3** - Armazenamento de mídia

### **Ferramentas de Desenvolvimento**
- **Git** - Controle de versão
- **Swagger** - Documentação da API
- **Sentry** - Monitoramento de erros
- **Redis** - Cache e sessões

## 📦 Estrutura do Projeto

```
indicaai/
├── ads/                    # Sistema de anúncios e necessidades
├── api/                    # API REST e documentação
├── budgets/               # Sistema de orçamentos
├── categories/            # Gestão de categorias
├── chat/                  # Sistema de mensagens
├── core/                  # Configurações e utilitários
├── notifications/         # Sistema de notificações
├── rankings/              # Sistema de avaliações
├── search/                # Busca avançada
├── users/                 # Gestão de usuários
├── static/                # Arquivos estáticos
├── templates/             # Templates HTML
├── media/                 # Upload de arquivos
└── requirements.txt       # Dependências Python
```

## ⚙️ Configuração do Ambiente

### **Pré-requisitos**
- Python 3.8+
- PostgreSQL 12+
- Redis
- Git

### **Instalação Local**

1. **Clone o repositório:**
```bash
git clone [repository-url]
cd necessito
```

2. **Crie o ambiente virtual:**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. **Instale as dependências:**
```bash
pip install -r requirements.txt
```

4. **Configure as variáveis de ambiente:**
```bash
cp core/settings/.env.example core/settings/.env
# Edite o arquivo .env com suas configurações
```

5. **Execute as migrações:**
```bash
python manage.py migrate
```

6. **Crie um superusuário:**
```bash
python manage.py createsuperuser
```

7. **Inicie o servidor:**
```bash
python manage.py runserver
```

### **Deploy com Docker**

```bash
# Build da imagem
docker build -t indicaai .

# Executar com docker-compose
docker-compose up -d
```

## 🔧 Comandos Úteis

### **Gestão de Dados**
```bash
# Importar categorias
python manage.py import_categories

# Atualizar geolocalizações
python manage.py atualizar_geolocalizacao_usuarios

# Backup do banco
./backup_config.sh
```

### **API e Documentação**
- **API Docs**: `/api/docs/`
- **Swagger UI**: `/api/swagger/`
- **Admin Panel**: `/admin/`

## 🔒 Segurança e Compliance

- ✅ **HTTPS** obrigatório em produção
- ✅ **LGPD** - Conformidade com proteção de dados
- ✅ **Autenticação** multi-fator disponível
- ✅ **Validação** rigorosa de dados
- ✅ **Rate limiting** em APIs
- ✅ **Logs** de auditoria completos

## 📊 Monitoramento e Métricas

- Dashboard de métricas em tempo real
- Relatórios de performance
- Monitoramento de uptime
- Análise de comportamento do usuário
- Alertas automatizados

## 🤝 Contribuição

Este é um projeto privado. Para contribuições:

1. Entre em contato com a equipe de desenvolvimento
2. Siga os padrões de código estabelecidos
3. Submeta pull requests para review
4. Mantenha a documentação atualizada

## 📧 Contato e Suporte

- **Email**: necessitobr@gmail.com
- **Website**: [necessito.online](https://necessito.online)
- **Suporte**: Através da plataforma

## 📄 Licença

© 2025 Indicaai - Marketplace. Todos os direitos reservados.

Este é um software proprietário. Seu uso, modificação ou distribuição não autorizada é estritamente proibida.

---

<div align="center">
  <strong>Desenvolvido com ❤️ pela equipe Indicaai</strong>
</div>
