\# 🏗️ Arquitetura VPS Ubuntu Multi-Aplicação

\#\# Diagrama da Arquitetura Atual

\`\`\`

Internet (HTTPS/HTTP \- Porta 80/443)

                    ↓

┌─────────────────────────────────────────────────────────────────────┐

│                        NGINX GLOBAL                                │

│                    (nginx-global)                                  │

│               Container: 315aca92d97b                              │

│           Rede: nginx-global\_global-network                        │

│               Portas: 80/443 → SSL Termination                    │

│                                                                    │

│  ┌─────────────────────────┐    ┌─────────────────────────────────┐│

│  │   necessito.online      │    │   urbanlive.com.br             ││

│  │   ↓ proxy\_pass          │    │   ↓ proxy\_pass                 ││

│  │   nginx-necessito:80    │    │   urbanlive\_web:8000           ││

│  └─────────────────────────┘    └─────────────────────────────────┘│

└─────────────────────────────────────────────────────────────────────┘

         │                                    │

         ▼                                    ▼

┌───────────────────────────────┐    ┌────────────────────────────────┐

│      NECESSITO (Indicai)      │    │        URBANLIVE V2            │

│      🛒 Marketplace B2B       │    │    🏘️ Zeladoria Colaborativa   │

│                               │    │                                │

│ ┌───────────────────────────┐ │    │ ┌────────────────────────────┐ │

│ │ nginx-necessito           │ │    │ │ urbanlive\_web              │ │

│ │ Container: 155a1ecd3002   │ │    │ │ Container: 759c0de23534    │ │

│ │ Porta: 80 (interna)      │ │    │ │ Porta: 8000→8001 (externa) │ │

│ │ Rede: global-network     │ │    │ │ Redes: engage\_hub\_default \+ │ │

│ └───────────────────────────┘ │    │ │        global-network      │ │

│              ↓                │    │ └────────────────────────────┘ │

│ ┌───────────────────────────┐ │    │              ↓                │

│ │ necessito-web\_prod-1      │ │    │ ┌────────────────────────────┐ │

│ │ Container: 918653163d1d   │ │    │ │ Django 5.0.1 \+ DRF \+ JWT  │ │

│ │ Porta: 8000 (interna)    │ │    │ │ API REST \+ WebSocket       │ │

│ │ Rede: necessito\_prod     │ │    │ └────────────────────────────┘ │

│ └───────────────────────────┘ │    │                                │

│              ↓                │    │ ┌────────────────────────────┐ │

│ ┌───────────────────────────┐ │    │ │ urbanlive\_db               │ │

│ │ Django 5.1.4 \+ PostgreSQL│ │    │ │ Container: e09300a390e4    │ │

│ │ API REST \+ WebSocket     │ │    │ │ PostgreSQL 15-alpine       │ │

│ └───────────────────────────┘ │    │ │ Porta: 5432→5433 (externa) │ │

│                               │    │ │ Rede: engage\_hub\_default   │ │

│ ┌───────────────────────────┐ │    │ └────────────────────────────┘ │

│ │ necessito-db\_prod-1       │ │    │                                │

│ │ Container: 5c745834ea3c   │ │    │ ┌────────────────────────────┐ │

│ │ PostgreSQL 17            │ │    │ │ urbanlive\_redis            │ │

│ │ Porta: 5432 (externa)    │ │    │ │ Container: d70cd237c622    │ │

│ │ Rede: necessito\_prod     │ │    │ │ Redis 7-alpine             │ │

│ └───────────────────────────┘ │    │ │ Porta: 6379→6380 (externa) │ │

└───────────────────────────────┘    │ │ Rede: engage\_hub\_default   │ │

                                     │ └────────────────────────────┘ │

                                     └────────────────────────────────┘

\`\`\`

\#\# 📊 Mapeamento de Containers Ativos

| \*\*Container ID\*\* | \*\*Nome\*\* | \*\*Imagem\*\* | \*\*Portas\*\* | \*\*Status\*\* | \*\*Função\*\* |

|------------------|----------|------------|------------|------------|------------|

| \*\*315aca92d97b\*\* | nginx-global | nginx:1.25-alpine | 80/443 | ✅ Ativo | Proxy reverso \+ SSL |

| \*\*155a1ecd3002\*\* | nginx-necessito | nginx:1.25-alpine | 80 | ✅ Ativo | Nginx Necessito |

| \*\*918653163d1d\*\* | necessito-web\_prod-1 | necessito-web\_prod | 8000 | ✅ Ativo | Django Necessito |

| \*\*5c745834ea3c\*\* | necessito-db\_prod-1 | postgres:17 | 5432 | ✅ Ativo | BD Necessito |

| \*\*759c0de23534\*\* | urbanlive\_web | engage\_hub\_web | 8000→8001 | ✅ Ativo | Django UrbanLive |

| \*\*e09300a390e4\*\* | urbanlive\_db | postgres:15-alpine | 5432→5433 | ✅ Ativo | BD UrbanLive |

| \*\*d70cd237c622\*\* | urbanlive\_redis | redis:7-alpine | 6379→6380 | ✅ Ativo | Cache UrbanLive |

\#\# 🌐 Redes Docker

| \*\*Rede\*\* | \*\*Função\*\* | \*\*Containers\*\* |

|----------|------------|----------------|

| \*\*nginx-global\_global-network\*\* | Comunicação global | nginx-global, nginx-necessito, urbanlive\_web |

| \*\*necessito\_app\_network\_prod\*\* | Rede interna Necessito | nginx-necessito, necessito-web\_prod-1, necessito-db\_prod-1 |

| \*\*engage\_hub\_default\*\* | Rede interna UrbanLive | urbanlive\_web, urbanlive\_db, urbanlive\_redis |

\#\# 🔌 Mapeamento de Portas

\#\#\# Externas (VPS → Internet)

\- \*\*80/443\*\* → nginx-global (HTTP/HTTPS \+ SSL)

\- \*\*5432\*\* → necessito-db\_prod-1 (PostgreSQL Necessito)

\- \*\*5433\*\* → urbanlive\_db (PostgreSQL UrbanLive)

\- \*\*6380\*\* → urbanlive\_redis (Redis UrbanLive)

\- \*\*8001\*\* → urbanlive\_web (Django UrbanLive)

\#\#\# Internas (Container → Container)

\- \*\*nginx-global:80/443\*\* → nginx-necessito:80, host:8001 (urbanlive)

\- \*\*nginx-necessito:80\*\* → necessito-web\_prod-1:8000

\- \*\*urbanlive\_web:8000\*\* → urbanlive\_db:5432, urbanlive\_redis:6379

\#\# 🎯 URLs de Produção

\- \*\*Necessito (Indicai):\*\* https://necessito.online → nginx-necessito:80 → necessito-web\_prod-1:8000

\- \*\*UrbanLive V2:\*\* https://urbanlive.com.br → host:8001 → urbanlive\_web:8000

\#\# ✅ Status de Conectividade

\- ✅ \*\*nginx-global\*\* → \*\*host:8001\*\* → \*\*urbanlive\_web\*\* (Corrigido: via porta externa)

\- ✅ \*\*nginx-global\*\* → \*\*nginx-necessito\*\* (Funcionando)

\- ✅ \*\*urbanlive\_web\*\* → \*\*urbanlive\_db\*\* (Funcionando)

\- ✅ \*\*urbanlive\_web\*\* → \*\*urbanlive\_redis\*\* (Funcionando)

\- ✅ \*\*necessito-web\*\* → \*\*necessito-db\*\* (Funcionando)

\---

\#\# 🔧 Últimas Correções Aplicadas

1\. \*\*Conectividade UrbanLive:\*\* Proxy nginx corrigido para usar porta externa \`host:8001\`

2\. \*\*Configuração Docker:\*\* Redes declaradas corretamente no docker-compose.yml

3\. \*\*502 Bad Gateway:\*\* Resolvido definitivamente \- funciona após docker-compose down/uproot@srv824627:\~\#

