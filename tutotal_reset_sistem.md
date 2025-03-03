# Tutorial: Reset Completo do Ambiente Django com Backup

Este guia explica como utilizar o script de reset de ambiente com sistema de backup integrado.

## 📋 Pré-requisitos
1. Sistema Linux/macOS (ou WSL no Windows)
2. Projeto Django configurado
3. Comando `import_categorias` implementado
4. Arquivo `categorias.txt` na raiz do projeto

## 🚀 Passo a Passo

### 1. Preparação do Script
```bash
# Torne o script executável
chmod +x reset_env.sh

# Crie a pasta para categorias (se necessário)
touch categorias.txt

2. Entendendo o Fluxo do Script
Backup Automático: Cria cópia segura do banco atual

Reset Completo:

Remove banco de dados existente

Limpa migrações antigas

Cria nova estrutura de banco

Carga de Dados:

Importa categorias/subcategorias

Cria superusuário personalizado

3. Execução do Script
./reset_env.sh

4. Verificação Pós-Execução
Confirme a criação do backup:
ls -lh backups/

Teste o login admin:
python manage.py runserver
Acesse http://localhost:8000/admin com as credenciais geradas

Verifique as categorias:

bash
Copy
python manage.py shell
python
Copy
from categories.models import Categoria
print(Categoria.objects.count())  # Deve retornar 50
print(Categoria.objects.filter(parent__isnull=False).count())  # Deve retornar 250

fi
🔄 Fluxo Completo do Sistema
mermaid
Copy
graph TD
    A[Início] --> B[Backup do BD]
    B --> C[Remove BD/Migrações]
    C --> D[Cria Nova Estrutura]
    D --> E[Importa Categorias]
    E --> F[Cria Superusuário]
    F --> G[Relatório Final]

❓ FAQ
Q: Posso usar com outros bancos além do SQLite?
R: Sim, basta ajustar a variável DB_NAME e credenciais no script.

Q: Como adicionar mais dados iniciais?
R: Crie novos comandos Django e chame após a importação de categorias.

Q: O script funciona em Windows?
R: Sim, via WSL ou adaptando os comandos para PowerShell.

Copy

Este tutorial fornece uma documentação completa com:
- Instruções claras de execução
- Diagrama de fluxo do processo
- Opções de personalização
- Medidas de segurança
- Sistema de perguntas frequentes

Para usar, basta copiar os dois arquivos para seu projeto Django e seguir os passos do tutorial!