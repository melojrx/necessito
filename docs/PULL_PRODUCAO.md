# 🔄 Pull em Produção - Indicaai

Este documento explica como atualizar o código em produção de forma segura e eficiente.

## 📋 Opções Disponíveis

### 1. Pull Rápido (Recomendado)

```bash
./pull_prod.sh
```

**Quando usar:** Para atualizações de código que não envolvem mudanças na infraestrutura.

**O que faz:**
- ✅ Cria backup automático do banco
- ✅ Faz pull do código do repositório
- ✅ Detecta automaticamente se precisa rebuild
- ✅ Executa migrações se necessário
- ✅ Coleta arquivos estáticos
- ✅ Reinicia apenas os serviços necessários
- ✅ Verifica se a aplicação está funcionando

### 2. Deploy Completo

```bash
./deploy_prod.sh
```

**Quando usar:** Para mudanças significativas na infraestrutura ou primeiro deploy.

**O que faz:**
- ✅ Deploy completo com rebuild de todas as imagens
- ✅ Recria todos os containers
- ✅ Executa todas as verificações

## 🔍 Detalhamento do Pull Rápido

### Verificações Automáticas

O script `pull_prod.sh` faz verificações inteligentes:

1. **Mudanças nos Requirements**
   ```bash
   # Detecta mudanças em:
   - requirements_base.txt
   - requirements_prod.txt
   - requirements_dev.txt
   ```

2. **Mudanças no Dockerfile**
   ```bash
   # Se detectar mudanças, faz rebuild automático
   ```

3. **Novas Migrações**
   ```bash
   # Detecta arquivos em */migrations/*.py
   # Executa automaticamente se necessário
   ```

### Processo Passo a Passo

1. **Verificação Inicial**
   - Verifica se está no diretório correto
   - Mostra branch atual
   - Alerta sobre mudanças não commitadas

2. **Backup de Segurança**
   ```bash
   # Cria backup automático
   backups/backup_pre_pull_YYYYMMDD_HHMMSS.sql
   ```

3. **Pull do Código**
   ```bash
   git pull origin <branch_atual>
   ```

4. **Análise de Mudanças**
   - Verifica se precisa rebuild
   - Verifica se há novas migrações

5. **Rebuild (se necessário)**
   ```bash
   docker-compose -f docker-compose_prod.yml build --no-cache web
   ```

6. **Migrações (se necessário)**
   ```bash
   docker-compose -f docker-compose_prod.yml run --rm web python manage.py migrate
   ```

7. **Arquivos Estáticos**
   ```bash
   docker-compose -f docker-compose_prod.yml run --rm web python manage.py collectstatic --noinput
   ```

8. **Reinicialização**
   ```bash
   # Reinicia apenas os serviços da aplicação
   docker-compose -f docker-compose_prod.yml restart web celery celery-beat nginx
   ```

9. **Verificação Final**
   - Testa se a aplicação responde
   - Mostra status dos containers
   - Exibe logs recentes se houver problemas

## 🚨 Cenários de Emergência

### Rollback Rápido

```bash
# Voltar para o commit anterior
git reset --hard HEAD~1

# Reiniciar serviços
docker-compose -f docker-compose_prod.yml restart web celery celery-beat nginx
```

### Restaurar Banco de Dados

```bash
# Listar backups disponíveis
ls -la backups/

# Restaurar backup específico
docker-compose -f docker-compose_prod.yml exec -T db psql -U postgres necessito_prod < backups/backup_pre_pull_YYYYMMDD_HHMMSS.sql
```

### Verificar Logs

```bash
# Logs em tempo real
docker-compose -f docker-compose_prod.yml logs -f web

# Logs específicos
docker-compose -f docker-compose_prod.yml logs --tail=50 web
docker-compose -f docker-compose_prod.yml logs --tail=50 nginx
docker-compose -f docker-compose_prod.yml logs --tail=50 celery
```

## 📊 Monitoramento Pós-Pull

### Verificações Essenciais

1. **Status dos Containers**
   ```bash
   docker-compose -f docker-compose_prod.yml ps
   ```

2. **Teste da Aplicação**
   ```bash
   curl -f http://localhost:8000/health/
   ```

3. **Verificar NGINX Global**
   ```bash
   # Se integrado com nginx-global
   curl -f https://necessito.online
   ```

4. **Logs de Erro**
   ```bash
   # Verificar se há erros recentes
   docker-compose -f docker-compose_prod.yml logs --since=5m web | grep -i error
   ```

### Métricas de Performance

```bash
# Uso de recursos
docker stats --no-stream

# Espaço em disco
df -h
docker system df
```

## 🔧 Comandos Úteis

### Gestão de Containers

```bash
# Status completo
docker-compose -f docker-compose_prod.yml ps

# Reiniciar serviço específico
docker-compose -f docker-compose_prod.yml restart web

# Parar todos os serviços
docker-compose -f docker-compose_prod.yml down

# Iniciar todos os serviços
docker-compose -f docker-compose_prod.yml up -d
```

### Gestão de Dados

```bash
# Backup manual
docker-compose -f docker-compose_prod.yml exec -T db pg_dump -U postgres necessito_prod > backup_manual.sql

# Limpar arquivos antigos
find backups/ -name "*.sql" -mtime +7 -delete
```

### Debug

```bash
# Entrar no container da aplicação
docker-compose -f docker-compose_prod.yml exec web bash

# Executar comando Django
docker-compose -f docker-compose_prod.yml exec web python manage.py shell

# Verificar configurações
docker-compose -f docker-compose_prod.yml exec web python manage.py check
```

## 📅 Boas Práticas

### Antes do Pull

1. **Verificar Status**
   ```bash
   git status
   git log --oneline -5
   ```

2. **Testar em Desenvolvimento**
   - Sempre teste as mudanças em dev primeiro
   - Execute os testes automatizados

3. **Comunicar a Equipe**
   - Informe sobre o deploy
   - Documente mudanças importantes

### Durante o Pull

1. **Monitorar Logs**
   - Acompanhe a saída do script
   - Verifique se há erros

2. **Verificar Backup**
   - Confirme que o backup foi criado
   - Anote o nome do arquivo

### Após o Pull

1. **Teste Funcional**
   - Acesse a aplicação
   - Teste funcionalidades críticas

2. **Monitorar por 15 minutos**
   - Observe logs de erro
   - Verifique performance

3. **Documentar**
   - Registre o que foi atualizado
   - Anote problemas encontrados

## 🚀 Automação Futura

### CI/CD Pipeline

Considere implementar:

```yaml
# .github/workflows/deploy.yml
name: Deploy to Production
on:
  push:
    branches: [main]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to server
        run: |
          ssh user@server 'cd /path/to/project && ./pull_prod.sh'
```

### Webhooks

```bash
# Endpoint para deploy automático
# POST /deploy/webhook/
```

---

**💡 Dica:** Use sempre o `pull_prod.sh` para atualizações rotineiras. É mais rápido e seguro que o deploy completo.