# Configuração MCP PostgreSQL

## Informações de Conexão

### Comando de Execução

```bash
npx -y postgres-mcp-server postgresql://postgres:postgres123@localhost:5432/necessito_dev
```

## Parâmetros da Conexão

- **Host:** `localhost` (ou `db` se dentro do container Docker)
- **Porta:** `5432`
- **Database:** `necessito_dev`
- **Usuário:** `postgres`
- **Senha:** `postgres123`
- **Schema:** `public`

## Formato da Connection String

```text
postgresql://[usuário]:[senha]@[host]:[porta]/[database]
```

**Nota:** O `postgres-mcp-server` detecta automaticamente todos os schemas disponíveis.

### Exemplo para Produção

⚠️ **ATENÇÃO:** Substitua os valores abaixo com as credenciais reais de produção

```bash
npx -y postgres-mcp-server postgresql://[USER_PROD]:[PASS_PROD]@[HOST_PROD]:[PORT]/necessito_prod
```

## Schemas Disponíveis

O `postgres-mcp-server` detecta automaticamente todos os schemas disponíveis no banco de dados.

Atualmente o banco possui:

- `public` - Schema padrão do PostgreSQL

### Verificar Schemas no Banco

Para listar os schemas disponíveis no banco de dados:

```bash
docker compose -f docker-compose_dev.yml exec db psql -U postgres -d necessito_dev -c "\dn"
```

Ou via SQL:

```sql
SELECT schema_name FROM information_schema.schemata;
```

## Uso com Docker

### De fora do container (desenvolvimento local)

```bash
npx -y postgres-mcp-server postgresql://postgres:postgres123@localhost:5432/necessito_dev
```

### De dentro do container (se necessário)

```bash
docker compose -f docker-compose_dev.yml exec web npx -y postgres-mcp-server postgresql://postgres:postgres123@db:5432/necessito_dev
```

## Troubleshooting

### Erro de Conexão

Se houver erro de conexão, verifique:

1. **Container do PostgreSQL está rodando:**
   ```bash
   docker compose -f docker-compose_dev.yml ps db
   ```

2. **Porta 5432 está exposta:**
   Verifique no arquivo `docker-compose_dev.yml` se a porta está mapeada

3. **Credenciais corretas:**
   Verifique o arquivo `.env` para confirmar as credenciais

### Testar Conexão Diretamente

```bash
docker compose -f docker-compose_dev.yml exec db psql -U postgres -d necessito_dev -c "SELECT version();"
```

## Integrações

### VS Code MCP

Se estiver usando a extensão MCP do VS Code, adicione ao arquivo de configuração:

```json
{
  "mcp.servers": {
    "postgres-necessito": {
      "command": "npx",
      "args": [
        "-y",
        "postgres-mcp-server",
        "postgresql://postgres:postgres123@localhost:5432/necessito_dev"
      ]
    }
  }
}
```

## Comandos Úteis

### Listar tabelas do schema public
```bash
docker compose -f docker-compose_dev.yml exec db psql -U postgres -d necessito_dev -c "\dt public.*"
```

### Listar views
```bash
docker compose -f docker-compose_dev.yml exec db psql -U postgres -d necessito_dev -c "\dv public.*"
```

### Estrutura de uma tabela
```bash
docker compose -f docker-compose_dev.yml exec db psql -U postgres -d necessito_dev -c "\d+ nome_da_tabela"
```

## Segurança

⚠️ **IMPORTANTE:**

1. Nunca commite credenciais de produção em repositórios
2. Use variáveis de ambiente para credenciais sensíveis
3. Considere criar um usuário específico com permissões limitadas para o MCP
4. Em produção, use conexões SSL quando possível

### Criar Usuário Read-Only (Recomendado para Produção)

```sql
-- Criar usuário read-only
CREATE USER mcp_readonly WITH PASSWORD 'senha_segura';

-- Dar permissão de conexão
GRANT CONNECT ON DATABASE necessito_dev TO mcp_readonly;

-- Dar permissão de uso do schema
GRANT USAGE ON SCHEMA public TO mcp_readonly;

-- Dar permissão de SELECT em todas as tabelas
GRANT SELECT ON ALL TABLES IN SCHEMA public TO mcp_readonly;

-- Garantir que futuras tabelas também tenham permissão
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO mcp_readonly;
```

Depois use:

```bash
npx -y postgres-mcp-server postgresql://mcp_readonly:senha_segura@localhost:5432/necessito_dev
```

---

**Última atualização:** 10 de novembro de 2025
