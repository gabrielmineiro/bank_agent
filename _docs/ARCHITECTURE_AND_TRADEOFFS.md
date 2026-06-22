# 🏗️ Decisões Arquiteturais e Trade-offs

A arquitetura deste projeto foi desenhada com foco em **Segurança (Security by Design)**, **Separação de Responsabilidades (Separation of Concerns)** e **Facilidade de Avaliação**. Abaixo estão detalhadas as principais decisões tomadas e os trade-offs envolvidos.

---

## 1. Arquitetura de Camadas (Monorepo vs. Microsserviços)

Optou-se por consolidar a solução em um monorepo estruturado em pastas modulares (`/agent`, `/mcp`, `/kb`, `/shared`).

> **Decisão:** As regras de negócio bancárias (`Services`) foram isoladas da inteligência artificial (`LangChain Tools`). As *Tools* atuam apenas como *wrappers* (adaptadores) que injetam as dependências nos serviços puros em Python.

> **Trade-off:** Embora em um ambiente de produção real o MCP pudesse ser uma API REST externa independente, emular os serviços localmente no monorepo elimina a necessidade de orquestração complexa (como múltiplos containers Docker), garantindo que qualquer desenvolvedor consiga testar o código com o mínimo de atrito.

---

## 2. Stack de LLM 100% Open-Source (Hugging Face & Qwen 2.5)

Considerando a sensibilidade dos dados no contexto bancário, o projeto foi desenvolvido para **não depender de APIs proprietárias** (como OpenAI ou Google Gemini).

> **Decisão:** A orquestração do Agente utiliza o modelo público `Qwen/Qwen2.5-7B-Instruct` via Hugging Face Inference API, escolhido por seu excelente desempenho nativo em *Tool Calling* e capacidade de seguir instruções restritas.

> **Trade-off:** Evitamos o *vendor lock-in* e garantimos custo zero de execução. No entanto, a API gratuita de inferência em nuvem possui *rate limits* e pode apresentar maior latência em horários de pico se comparada a soluções comerciais pagas.

---

## 3. Controle de Acesso (RBAC) na Camada de Orquestração

A segurança e a autorização **não foram delegadas ao LLM**.

> **Decisão:** Implementação do conceito de *Guardrails* Dinâmicos. As ferramentas são filtradas no nível da aplicação Python antes de serem entregues ao Agente, com base na `role` do usuário autenticado (`customer`, `manager`, `admin`).

> **Trade-off:** O LLM economiza tokens e reduz a latência, pois não tenta "raciocinar" sobre ferramentas que não pode usar. O trade-off é que a matriz de permissões deve ser rigorosamente mantida na camada de inicialização do Agente.

---

## 4. RAG com Processamento Local (ChromaDB)

Para a Base de Conhecimento, optou-se por **não utilizar bancos vetoriais em nuvem** ou que exigissem infraestrutura pesada (como OpenSearch).

> **Decisão:** Utilização do ChromaDB operando no modo *serverless* com persistência em disco (arquivos locais em `/data/chroma_db`), combinado com embeddings processados localmente via `HuggingFaceEmbeddings` (modelo `all-MiniLM-L6-v2`).

> **Trade-off:** Facilita o setup e a portabilidade do projeto (basta clonar e rodar). O trade-off é que essa configuração SQLite-based atende perfeitamente à leitura de PDFs regulatórios em pequena escala, mas não seria escalável para indexar milhões de documentos em um cenário de *Big Data*.

---

## 5. Separação entre Observabilidade e Auditoria Crítica

Métricas de IA e logs de negócios têm finalidades e destinos diferentes.

> **Decisão:**
> - **Observabilidade** (`LangChain Callbacks`): o rastreamento de tempo, uso de ferramentas e tokens foi implementado de forma **passiva** (escutando os eventos do orquestrador), para não poluir o código de negócio.
> - **Auditoria** (`Services`): a geração do log transacional (`user`, `action`, `amount`, `timestamp`) foi acoplada de forma **ativa e obrigatória** diretamente nos métodos de alteração de estado (ex: `create_pix`), persistindo em `data/audit.log`.

> **Trade-off:** Essa abordagem dupla exige a manutenção de dois sistemas de registro distintos. Contudo, garante que, mesmo que o LLM sofra uma falha ou "alucine", uma transação financeira só será auditada no arquivo de segurança se a mutação no banco de dados for efetivamente confirmada.