# 🚀 Próximos Passos e Evolução do Projeto

Embora este projeto atenda a todos os requisitos do desafio técnico com uma arquitetura sólida, a transição de uma **Prova de Conceito (PoC)** para um ambiente de **produção real (Enterprise)** exigiria as seguintes evoluções:

---

## 1. Segurança e Autenticação (Identity Provider)

**Implementação de JWT/OAuth2:** Atualmente, a sessão do usuário (`user_id` e `role`) é injetada estaticamente no código para fins de teste. O próximo passo seria integrar a aplicação a um provedor de identidade real (ex: Keycloak, AWS Cognito) e extrair essas *claims* diretamente do token JWT no header da requisição.

**Criptografia de Logs:** Mascarar dados sensíveis (PII) nos logs de telemetria e aplicar criptografia em repouso no arquivo `audit.log`.

---

## 2. Escalabilidade e Infraestrutura

**Conteinerização e CI/CD:** Empacotar a aplicação em imagens Docker (separando o backend do banco vetorial) e criar pipelines do GitHub Actions para testes automatizados e deploy em clusters Kubernetes.

**Migração do Banco de Dados:** Substituir os dicionários em memória (Mock DB) e o ChromaDB local por soluções gerenciadas e escaláveis, como PostgreSQL (para transações ACID) e Pinecone ou Qdrant (para busca vetorial em milhões de documentos).

---

## 3. Otimização de IA e UX

**Streaming de Respostas (WebSockets):** Implementar o envio de tokens em tempo real para o usuário (efeito máquina de escrever). Isso reduz drasticamente a percepção de latência, especialmente ao usar modelos Open-Source hospedados.

**Cache Semântico (Semantic Caching):** Adicionar uma camada de cache (ex: Redis + LangChain Cache) para respostas idênticas ou semanticamente similares, economizando tempo de processamento e requisições à API do LLM em perguntas frequentes (como "Qual a taxa do PIX?").

**Avaliação de RAG:** Implementar um pipeline de testes automatizados focado em LLMs para medir métricas de precisão, relevância e alucinação do RAG a cada nova versão do modelo ou atualização dos PDFs de tarifas.

---

## 4. System Prompt e Human-in-the-Loop

### Refatorações no System Prompt

O system prompt atual funciona corretamente, mas poderia ser aprimorado em algumas frentes:

- **Separação de responsabilidades no prompt:** Dividir o bloco único de instruções em seções explicitamente rotuladas (ex: `[IDENTIDADE]`, `[REGRAS DE SEGURANÇA]`, `[FORMATO DE RESPOSTA]`), o que melhora a aderência do modelo às instruções em cadeia longa de mensagens.

- **Few-shot examples:** Incluir exemplos concretos de interações corretas (especialmente para confirmação de PIX e citação de fontes do RAG) diretamente no prompt, reduzindo ambiguidade e alucinações em edge cases.

- **Instruções de fallback mais explícitas:** Detalhar o comportamento esperado quando uma ferramenta retorna erro ou resultado vazio, evitando que o modelo improvise respostas fora do escopo bancário.

- **Chain-of-thought guiado:** Para operações críticas, instruir o modelo a externalizar seu raciocínio em um passo interno antes de acionar a ferramenta, tornando o fluxo mais auditável e reduzindo erros de interpretação.

### Limitação do Human-in-the-Loop com LangChain

A implementação atual do *human-in-the-loop* — onde o agente solicita confirmação do usuário antes de executar operações críticas como PIX — **foi feita via instrução no system prompt e via input do usuário direto no service**, e não via controle de fluxo real. Isso significa que a confirmação é tratada pelo próprio LLM como parte da conversa, sem que a execução da ferramenta seja de fato interrompida e aguardada.

A solução robusta para esse caso seria o uso de **LangGraph**, que oferece suporte nativo a `interrupt_before` e `interrupt_after` em nós do grafo, permitindo pausar o fluxo de execução, aguardar input humano e só então retomar — com total controle programático sobre o estado.

> **Por que não foi implementado com LangGraph:** Migrar de `AgentExecutor` (LangChain clássico) para um grafo LangGraph representaria uma refatoração arquitetural significativa do projeto, o que fugiria do escopo do desafio. A decisão foi manter o `AgentExecutor` e garantir o comportamento via prompt, documentando a limitação de forma transparente para evolução futura.