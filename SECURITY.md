# 🔒 Guia de Segurança - Necessito

## 📋 Configurações Protegidas

### ✅ Arquivos Protegidos pelo Git
- `.env` - Variáveis de ambiente sensíveis
- `core/settings/local.py` - Configurações locais
- `core/settings/production.py` - Configurações de produção
- `backups/config/` - Backups de configuração

### 🔧 Configuração Inicial

1. **Copie o template de ambiente:**
   ```bash
   cp .env.example .env
   ```

2. **Edite o arquivo .env com suas configurações:**
   ```bash
   nano .env  # ou use seu editor preferido
   ```

3. **Gere uma nova SECRET_KEY:**
   ```python
   python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
   ```

## 🛡️ Práticas de Segurança

### 📁 Backup Automático
Execute regularmente o script de backup:
```bash
./backup_config.sh
```

### 🔄 Restauração de Backup
Para restaurar configurações:
```bash
cp backups/config/.env_backup_YYYYMMDD_HHMMSS .env
```

### ⚠️ NUNCA Faça
- ❌ Commit do arquivo `.env`
- ❌ Compartilhe senhas em texto plano
- ❌ Use a mesma SECRET_KEY em produção e desenvolvimento
- ❌ Deixe DEBUG=True em produção

### ✅ SEMPRE Faça
- ✅ Use o `.env.example` como template
- ✅ Faça backup das configurações
- ✅ Use senhas fortes
- ✅ Mantenha as dependências atualizadas

## 🚨 Em Caso de Comprometimento

1. **Mude imediatamente:**
   - SECRET_KEY do Django
   - Senhas do banco de dados
   - Chaves de API (reCAPTCHA, etc.)

2. **Execute um novo backup:**
   ```bash
   ./backup_config.sh
   ```

3. **Verifique os logs:**
   ```bash
   docker logs necessito-web-1
   ```

## 📞 Contato
Em caso de problemas de segurança, entre em contato com a equipe de desenvolvimento. 