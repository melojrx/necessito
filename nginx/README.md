# 🌐 Configuração NGINX - Indicaai

Este diretório contém as configurações do NGINX para os ambientes de desenvolvimento e produção do projeto Necessito.

## 🏗️ Arquitetura VPS Multi-Aplicação

O projeto está integrado em uma VPS Ubuntu com múltiplas aplicações usando a seguinte arquitetura:

```
Internet → nginx-global (SSL/HTTPS) → nginx-necessito:80 → necessito-web_prod-1:8000
```

- **nginx-global**: Gerencia SSL/HTTPS e roteamento entre aplicações
- **nginx-necessito**: Proxy local para a aplicação Necessito
- **necessito-web_prod-1**: Container Django da aplicação

## 📁 Arquivos

- `dev.conf` - Configuração para desenvolvimento
- `prod.conf` - Configuração para produção (integrada com nginx-global)
- `README.md` - Esta documentação

## 🔧 Configurações

### Desenvolvimento (`dev.conf`)

**Características:**
- Escuta na porta 80 (HTTP apenas)
- Proxy reverso para o serviço `web` do Django (porta 8000)
- Servir arquivos estáticos e de mídia
- Suporte a WebSockets para Django Channels
- Configurações de timeout e tamanho máximo de corpo de requisição

### Produção (`prod.conf`)

**Características:**
- Escuta apenas na porta 80 (HTTP)
- **SSL gerenciado pelo nginx-global** (não localmente)
- Cabeçalhos de segurança (X-Frame-Options, etc.)
- Compressão Gzip
- Proxy reverso para o serviço `web` do Django (porta 8000)
- Servir arquivos estáticos e de mídia com cache otimizado
- Suporte a WebSockets
- Rate limiting para API
- Health check endpoint
- Configurações de timeout e tamanho máximo de corpo de requisição

## Desenvolvimento

Para desenvolvimento, o NGINX atua como proxy reverso para o Django:

```bash
# Iniciar ambiente de desenvolvimento
./setup_dev.sh

# Acessar aplicação
http://localhost
```

### Características do ambiente de desenvolvimento:
- HTTP apenas (porta 80)
- Proxy reverso para Django (porta 8000)
- Servir arquivos estáticos e media
- Suporte a WebSockets para Django Channels
- Hot reload do código Django

## Produção

Para produção, o NGINX inclui:

### Características:
- HTTP (porta 80) com redirecionamento para HTTPS
- HTTPS (porta 443) com certificados SSL
- Proxy reverso para Django com Gunicorn
- Compressão Gzip
- Headers de segurança
- Cache de arquivos estáticos
- Rate limiting para API
- Suporte a WebSockets

### Configuração SSL (Primeira vez)

1. **Editar domínio e email:**
   ```bash
   # Editar o arquivo init-letsencrypt.sh
   nano init-letsencrypt.sh
   
   # Alterar:
   domains=(necessito.online www.necessito.online)
   email="seu-email@exemplo.com"
   ```

2. **Configurar DNS:**
   - Aponte os domínios para o IP do servidor
   - Aguarde propagação DNS (pode levar até 24h)

3. **Executar configuração SSL:**
   ```bash
   ./init-letsencrypt.sh
   ```

## 🚀 Deploy em Produção

### Integração com nginx-global

1. **Verifique a rede global:**
   ```bash
   docker network ls | grep nginx-global
   ```

2. **Configure o proxy no nginx-global:**
   O nginx-global deve ter uma configuração similar a:
   ```nginx
   location / {
       proxy_pass http://nginx-necessito:80;
       proxy_set_header Host $host;
       proxy_set_header X-Real-IP $remote_addr;
       proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
       proxy_set_header X-Forwarded-Proto $scheme;
   }
   ```

3. **Inicie os serviços:**
   ```bash
   ./deploy_prod.sh
   ```

### SSL/HTTPS

- **SSL é gerenciado pelo nginx-global**, não pelo nginx-necessito
- Certificados Let's Encrypt são configurados no nginx-global
- O nginx-necessito recebe apenas tráfego HTTP interno

## Estrutura de Diretórios

```
nginx/
├── dev.conf          # Configuração desenvolvimento
├── prod.conf         # Configuração produção
└── README.md         # Esta documentação

data/
└── certbot/
    ├── conf/         # Certificados SSL
    └── www/          # Challenge files
```

## Logs

```bash
# Logs do NGINX
docker-compose -f docker-compose_prod.yml logs nginx

# Logs do Certbot
docker-compose -f docker-compose_prod.yml logs certbot

# Logs em tempo real
docker-compose -f docker-compose_prod.yml logs -f nginx
```

## Troubleshooting

### Problema: Certificado SSL não funciona
1. Verificar se DNS está apontando corretamente
2. Verificar logs do Certbot
3. Testar com staging=1 no init-letsencrypt.sh

### Problema: 502 Bad Gateway
1. Verificar se container Django está rodando
2. Verificar logs do Django
3. Verificar conectividade entre containers

### Problema: Arquivos estáticos não carregam
1. Verificar se collectstatic foi executado
2. Verificar volumes no docker-compose
3. Verificar permissões dos arquivos

## Configurações Personalizadas

Para personalizar as configurações:

1. **Alterar domínio:**
   - Editar `prod.conf`
   - Editar `init-letsencrypt.sh`
   - Atualizar `.env.prod`

2. **Adicionar novos domínios:**
   - Adicionar em `server_name` no `prod.conf`
   - Adicionar no array `domains` do `init-letsencrypt.sh`

3. **Configurar rate limiting:**
   - Ajustar `limit_req_zone` no `prod.conf`
   - Personalizar limites por endpoint

## 📊 Monitoramento

### Logs

```bash
# Logs do nginx-necessito
docker logs nginx-necessito

# Logs do nginx-global
docker logs nginx-global

# Logs em tempo real
docker-compose -f docker-compose_prod.yml logs -f nginx

# Verificar conectividade
docker exec nginx-necessito nginx -t
```

### Verificações

- **Status da aplicação:** `curl http://nginx-necessito/health/`
- **Conectividade entre redes:** `docker network inspect nginx-global_global-network`
- **SSL/HTTPS:** Gerenciado pelo nginx-global (container 315aca92d97b)

```bash
# Status dos containers
docker-compose -f docker-compose_prod.yml ps
```

## 🔄 Atualizações em Produção

### Pull Rápido (Recomendado)

```bash
# Script otimizado para atualizações de código
./pull_prod.sh
```

**Características:**
- ✅ Backup automático do banco
- ✅ Detecção inteligente de mudanças
- ✅ Rebuild apenas se necessário
- ✅ Migrações automáticas
- ✅ Reinicialização seletiva de serviços
- ✅ Verificação de saúde da aplicação

### Deploy Completo

```bash
# Para mudanças significativas na infraestrutura
./deploy_prod.sh
```

### Comandos de Emergência

```bash
# Rollback rápido
git reset --hard HEAD~1
docker-compose -f docker-compose_prod.yml restart web nginx

# Restaurar backup do banco
docker-compose -f docker-compose_prod.yml exec -T db psql -U postgres necessito_prod < backups/backup_YYYYMMDD_HHMMSS.sql

# Verificar logs de erro
docker-compose -f docker-compose_prod.yml logs --since=5m web | grep -i error
docker-compose -f docker-compose_prod.yml ps

# Uso de recursos
docker stats
```