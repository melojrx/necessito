### **Guia Definitivo de Regras de Negócio: Marketplace Indicai**

**Versão:** Final 1.0 **Data:** 12 de julho de 2025 

**Propósito:** Este documento detalha o ciclo de vida completo das operações, as regras de negócio, os status das entidades e os sistemas de comunicação da plataforma Indicai. Ele deve ser utilizado como a fonte central de verdade para o desenvolvimento, manutenção e gestão da ferramenta.

### **1\. Visão Geral e Atores**

O Indicai funciona como uma plataforma de licitação privada que conecta dois tipos de usuários:

* **Cliente:** Pessoa física ou jurídica que publica uma necessidade de serviço ou produto através de um **Anúncio**.  
* **Fornecedor:** Pessoa física ou jurídica qualificada que responde a esses anúncios com propostas comerciais, chamadas de **Orçamentos**.

### **2\. Entidades Centrais e Seus Status**

A operação da plataforma gira em torno de duas entidades principais: `Anúncio` e `Orçamento`. Seus status determinam o fluxo de trabalho e as ações possíveis em cada etapa.

#### **2.1. Status do Anúncio**

| Status | Descrição |
| ----- | ----- |
| `ativo` | Publicado e visível. Aguardando o recebimento do primeiro orçamento. |
| `analisando_orcamentos` | Já recebeu pelo menos um orçamento. O cliente está analisando as propostas. |
| `aguardando_confirmacao` | Cliente aceitou um orçamento. Aguardando a confirmação do fornecedor. O anúncio fica "travado", impedindo outras ações de aceite. |
| `em_atendimento` | O negócio foi fechado (orçamento aceito por ambos). O serviço está em andamento. |
| `finalizado` | O serviço foi concluído e o cliente marcou como finalizado. O sistema de avaliação é liberado. |
| `cancelado` | O cliente cancelou o anúncio antes de um negócio ser fechado. |
| `expirado` | O anúncio atingiu sua data de validade sem fechar negócio e foi encerrado pelo sistema. |
| `em_disputa` | Cliente ou fornecedor sinalizou um problema durante a fase de `em_atendimento`, requerendo mediação da plataforma. |

#### **2.2. Status do Orçamento**

| Status | Descrição |
| ----- | ----- |
| `enviado` | O fornecedor enviou a proposta e o cliente pode analisá-la. |
| `aceito_pelo_cliente` | O cliente selecionou este orçamento e aguarda a confirmação do fornecedor. |
| `confirmado` | **Orçamento Vencedor.** O fornecedor confirmou o aceite do cliente. |
| `rejeitado_pelo_cliente` | O cliente não aceitou o orçamento. Fim do fluxo para esta proposta. |
| `recusado_pelo_fornecedor` | O fornecedor não pôde confirmar o aceite do cliente após este tê-lo escolhido. |
| `cancelado_pelo_fornecedor` | O fornecedor retirou o orçamento antes de qualquer decisão do cliente. |
| `finalizado` | O serviço atrelado a este orçamento foi concluído (Anúncio foi `finalizado`). |
| `anuncio_cancelado` | O orçamento foi invalidado porque o anúncio correspondente foi cancelado pelo cliente. |
| `anuncio_expirado` | O orçamento foi invalidado porque o anúncio correspondente expirou. |

### **3\. Mapeamento Completo do Fluxo (Lifecycle)**

Esta seção descreve a jornada completa de uma transação, integrando as mudanças de status e as notificações automáticas.

**Etapa 1: Criação do Anúncio**

1. **Ação:** Cliente publica um novo `Anúncio`.  
2. **Status Inicial:** `Anúncio` \-\> `ativo`.  
3. **Notificação:**  
   * **Canal:** E-mail.  
   * **Destinatário:** Fornecedores com categorias de interesse correspondentes.  
   * **Mensagem:** "Um novo anúncio na categoria '\[Categoria\]' foi publicado e pode te interessar\!"

**Etapa 2: Recebimento de Orçamentos**

1. **Ação:** Fornecedor envia um `Orçamento`.  
2. **Mudança de Status:**  
   * `Orçamento` \-\> `enviado`.  
   * `Anúncio`: `ativo` \-\> `analisando_orcamentos` (apenas no primeiro orçamento recebido).  
3. **Notificação:**  
   * **Canal:** Alerta na Interface \+ E-mail.  
   * **Destinatário:** Cliente.  
   * **Mensagem:** "Você recebeu uma nova proposta para o anúncio '\[Nome do Anúncio\]'." (Tipo: `NOVO_ORCAMENTO`)

**Etapa 3: Análise e Decisão do Cliente**

1. **Ação:** Cliente analisa os orçamentos recebidos.  
2. **Cenário A: Cliente Rejeita um Orçamento**  
   * **Mudança de Status:** `Orçamento` \-\> `rejeitado_pelo_cliente`.  
   * **Notificação:**  
     * **Canal:** Alerta na Interface \+ E-mail.  
     * **Destinatário:** Fornecedor do orçamento rejeitado.  
     * **Mensagem:** "Sua proposta para '\[Nome do Anúncio\]' não foi selecionada pelo cliente." (Tipo: `ORCAMENTO_REJEITADO`)  
3. **Cenário B: Cliente Aceita um Orçamento**  
   * **Mudança de Status:**  
     * `Orçamento` escolhido \-\> `aceito_pelo_cliente`.  
     * `Anúncio` \-\> `aguardando_confirmacao`.  
   * **Regra Crítica:** Os demais orçamentos com status `enviado` permanecem inalterados, mas temporariamente bloqueados para aceite.  
   * **Notificação:**  
     * **Canal:** Alerta na Interface \+ E-mail (alta prioridade).  
     * **Destinatário:** Fornecedor do orçamento aceito.  
     * **Mensagem:** "Ação necessária: Sua proposta para '\[Nome do Anúncio\]' foi aceita\! Por favor, confirme o atendimento para fechar o negócio." (Tipo: `ORCAMENTO_ACEITO`)

**Etapa 4: Confirmação do Fornecedor**

1. **Ação:** Fornecedor notificado decide se confirma ou recusa o serviço.  
2. **Cenário A: Fornecedor Confirma (Negócio Fechado)**  
   * **Mudança de Status:**  
     * `Orçamento` vencedor \-\> `confirmado`.  
     * `Anúncio` \-\> `em_atendimento`.  
     * Demais orçamentos (`enviado`) \-\> `rejeitado_pelo_cliente`.  
   * **Notificação:**  
     * **Canal:** Alerta na Interface \+ E-mail.  
     * **Destinatário:** Cliente.  
     * **Mensagem:** "Negócio fechado\! O fornecedor '\[Nome do Fornecedor\]' confirmou o atendimento. O serviço para '\[Nome do Anúncio\]' já pode começar."  
3. **Cenário B: Fornecedor Recusa**  
   * **Mudança de Status:**  
     * `Orçamento` recusado \-\> `recusado_pelo_fornecedor`.  
     * `Anúncio` \-\> `analisando_orcamentos` (retorna ao estado anterior).  
   * **Regra Crítica:** O sistema desbloqueia os outros orçamentos `enviado`, permitindo que o cliente escolha uma nova opção.  
   * **Notificação:**  
     * **Canal:** Alerta na Interface \+ E-mail.  
     * **Destinatário:** Cliente.  
     * **Mensagem:** "Atenção: O fornecedor '\[Nome do Fornecedor\]' não pôde confirmar o serviço. Seu anúncio está ativo novamente para você escolher outra proposta."

**Etapa 5: Finalização e Sistema de Avaliação 360°**

1. **Ação:** Após a conclusão do serviço, o cliente marca o anúncio como finalizado.  
2. **Mudança de Status:**  
   * `Anúncio` \-\> `finalizado`.  
   * `Orçamento` vencedor \-\> `finalizado`.  
3. **Gatilho de Avaliação:** A mudança de status para `finalizado` **automaticamente libera o sistema de avaliação mútua** para o cliente e o fornecedor envolvidos.  
4. **Notificação de Finalização:**  
   * **Canal:** Alerta na Interface \+ E-mail.  
   * **Destinatário:** Fornecedor vencedor.  
   * **Mensagem:** "Serviço concluído\! O anúncio '\[Nome do Anúncio\]' foi finalizado. Por favor, deixe uma avaliação para o cliente." (Tipo: `ANUNCIO_FINALIZADO`)  
5. **Notificações de Avaliação:**  
   * Quando uma parte avalia a outra, a parte avaliada recebe uma notificação.  
   * **Canal:** Alerta na Interface \+ E-mail.  
   * **Destinatário:** Usuário avaliado (Cliente ou Fornecedor).  
   * **Mensagem:** "Você recebeu uma nova avaliação de '\[Nome do Avaliador\]' referente ao serviço '\[Nome do Anúncio\]'." (Tipo: `NOVA_AVALIACAO`)

### **4\. Regras de Negócio e Casos Especiais**

* **Edição de Conteúdo:**  
  * **Anúncios:** Não podem ser editados após receberem o primeiro orçamento (`analisando_orcamentos`). A única opção é cancelar e criar um novo para garantir a integridade das propostas.  
  * **Orçamentos:** Não podem ser editados. A política é **cancelar e reenviar**, garantindo um registro claro e imutável das propostas.  
* **Cancelamentos:**  
  * **Pelo Cliente:** Um `Anúncio` pode ser cancelado a qualquer momento antes do status `em_atendimento`. Ao ser cancelado, o anúncio vai para `cancelado` e todos os orçamentos atrelados mudam para `anuncio_cancelado`.  
  * **Pelo Fornecedor:** Um `Orçamento` (`enviado`) pode ser retirado a qualquer momento antes de ser aceito pelo cliente (`aceito_pelo_cliente`). Ele muda para `cancelado_pelo_fornecedor`. Se este for o último orçamento ativo, o `Anúncio` retorna de `analisando_orcamentos` para `ativo`.  
* **Timeout e Expiração:**  
  * Todo `Anúncio` tem uma data de validade. Se essa data for atingida antes de o anúncio chegar em `em_atendimento`, seu status muda para `expirado`, e os orçamentos atrelados mudam para `anuncio_expirado`.  
* **Gestão de Disputas:**  
  * Se houver um problema durante a fase de `em_atendimento`, qualquer uma das partes pode abrir uma disputa.  
  * Isso move o `Anúncio` e o `Orçamento` vencedor para o status `em_disputa`, congelando outras ações (como finalização e avaliação) e notificando os administradores da plataforma para mediação.  
* **Comunicação via Chat:**  
  * A funcionalidade de chat direto entre cliente e fornecedor é **habilitada exclusivamente** quando o `Anúncio` atinge o status `em_atendimento`.  
  * Cada nova mensagem no chat dispara uma notificação de `Alerta na Interface` para o destinatário. (Tipo: `NOVA_MENSAGEM_CHAT`)

### **5\. Tabela Resumo de Notificações**

| Evento do Sistema | Destinatário | Canal(is) | Tipo de Notificação (para o sistema) |
| ----- | ----- | ----- | ----- |
| Anúncio novo criado | Fornecedores (por categoria) | E-mail | `NOVO_ANUNCIO` |
| Orçamento novo enviado | Cliente | Alerta na UI, E-mail | `NOVO_ORCAMENTO` |
| Orçamento aceito pelo Cliente | Fornecedor | Alerta na UI, E-mail | `ORCAMENTO_ACEITO` |
| Orçamento rejeitado pelo Cliente | Fornecedor | Alerta na UI, E-mail | `ORCAMENTO_REJEITADO` |
| Orçamento confirmado pelo Fornecedor | Cliente | Alerta na UI, E-mail | `ORCAMENTO_CONFIRMADO` |
| Orçamento recusado pelo Fornecedor | Cliente | Alerta na UI, E-mail | `ORCAMENTO_RECUSADO` |
| Anúncio finalizado pelo Cliente | Fornecedor | Alerta na UI, E-mail | `ANUNCIO_FINALIZADO` |
| Nova avaliação recebida | Usuário Avaliado | Alerta na UI, E-mail | `NOVA_AVALIACAO` |
| Nova mensagem no Chat | Destinatário da Mensagem | Alerta na UI | `NOVA_MENSAGEM_CHAT` |

