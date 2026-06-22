# 🏦 Bank Agent — Guia de Configuração

Este guia cobre todo o processo para configurar e rodar o projeto localmente, do zero.

---

## Pré-requisitos

Antes de começar, certifique-se de ter instalado:

- **Python 3.10+** — [python.org/downloads](https://www.python.org/downloads/)
- **pip** (já vem com o Python)
- **Git** — [git-scm.com](https://git-scm.com/)

---

## Passo 1 — Clonar o repositório

```bash
git clone https://github.com/seu-usuario/bank_agent.git
cd bank_agent
```

---

## Passo 2 — Criar e ativar o ambiente virtual

Crie um ambiente virtual isolado para o projeto:

```bash
# Criar o ambiente virtual
python -m venv venv
```

Ative o ambiente:

```bash
# Windows (PowerShell)
.\venv\Scripts\Activate.ps1

# Windows (CMD)
.\venv\Scripts\activate.bat

# Linux / macOS
source venv/bin/activate
```

> Você saberá que o ambiente está ativo quando o prompt do terminal exibir `(venv)` no início.

---

## Passo 3 — Instalar as dependências

Com o ambiente virtual ativo, instale todas as dependências do projeto:

```bash
pip install -r requirements.txt
```

Em seguida, instale o próprio pacote em modo editável (necessário para que os imports entre módulos — `agent`, `mcp`, `kb`, `shared` — funcionem corretamente):

```bash
pip install -e .
```

---

## Passo 4 — Configurar as variáveis de ambiente

Copie o arquivo de exemplo e preencha com suas credenciais:

```bash
# Windows (PowerShell)
Copy-Item .env.example .env

# Linux / macOS
cp .env.example .env
```

Abra o arquivo `.env` e preencha os valores:

```env
# API KEY do Hugging Face. (enviada por email)

HUGGINGFACEHUB_API_TOKEN=XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

# Modelo de embeddings a ser usado para a base de conhecimento (RAG)
# Exemplo: all-MiniLM-L6-v2
EMBED_MODEL=all-MiniLM-L6-v2
```

> ⚠️ **Nunca versione o arquivo `.env`** — ele já está listado no `.gitignore`.

---

## Passo 5 — Configurar a Base de Conhecimento (RAG)

O agente possui uma base de conhecimento baseada em documentos PDF (ex: regulamentos, tarifas, políticas do banco). Se você deseja habilitar essa funcionalidade:


1. Execute o script de ingestão para processar os PDFs e gerar o banco vetorial (ChromaDB):

   ```bash
   python -m kb.setup_rag
   ```

   O índice vetorial será salvo automaticamente em `data/chroma_db/`.

> Se pular este passo, o agente simplesmente não terá acesso à ferramenta `search_knowledge_base`.

---

## Passo 6 — Rodar o agente

Com tudo configurado, inicie a sessão interativa do agente:

```bash
python -m agent.agent
```

O terminal irá solicitar:

```
=== INICIANDO SESSÃO BANCÁRIA ===

👤 ID do Usuário: (IDs de teste disponíveis '123', '456')
👤 Role ['manager', 'admin', 'customer']: 
```

| Role        | Permissões                                                               |
|-------------|--------------------------------------------------------------------------|
| `customer`  | Consulta dados e realiza operações da **própria conta** apenas           |
| `manager`   | Pode consultar e operar em contas de clientes                            |
| `admin`     | Acesso completo, incluindo ferramentas privilegiadas                     |

Após o login, você pode interagir com o agente normalmente:

```
👤 Prompt: Qual é o meu saldo?
🤖 Agente Processando...
🏦 ItaúBot: Seu saldo atual é de R$ 5.230,00.

👤 Prompt: sair
```

> Digite `sair`, `exit` ou `quit` para encerrar a sessão.

---

## Estrutura do Projeto

```
bank_agent/
├── agent/              # Definição do agente LangChain (LLM + prompt + executor)
│   ├── agent.py        # Entrypoint principal — rode este arquivo
│   └── telemetry.py    # Callback de observabilidade
├── mcp/                # Ferramentas (tools) disponíveis para o agente
│   ├── agent_tools.py  # Montagem das tools por perfil de usuário
│   ├── base_tools.py   # Ferramentas base (saldo, limite, PIX, RAG)
│   ├── priviled_tools.py # Ferramentas exclusivas para admin/manager
│   ├── database/       # Banco de dados mock
│   └── services/       # Lógica de negócio (Customer, Card, Transfer)
├── kb/                 # Base de conhecimento (RAG)
│   └── setup_rag.py    # Ingestão de PDFs e busca vetorial via ChromaDB
├── shared/             # Utilitários compartilhados
│   ├── permissions.py  # Decorator de controle de acesso por role
│   ├── audit.py        # Log de auditoria de operações
│   └── logger.py       # Logger estruturado
├── data/               # Dados gerados em runtime (não versionados)
│   ├── pdfs/           # PDFs para a base de conhecimento
│   └── chroma_db/      # Índice vetorial gerado pelo setup_rag.py
├── .env.example        # Template das variáveis de ambiente
├── requirements.txt    # Dependências Python
└── pyproject.toml      # Configuração do pacote
```

---

## Solução de Problemas

### `ModuleNotFoundError: No module named 'agent'` (ou `mcp`, `kb`, `shared`)
Você provavelmente não instalou o pacote em modo editável. Execute:
```bash
pip install -e .
```

### `ValidationError` ou erro de autenticação no Hugging Face
Verifique se o arquivo `.env` existe na raiz do projeto e se o token `HUGGINGFACEHUB_API_TOKEN` está correto e com permissão de leitura nos modelos desejados.

### `No PDFs found` ao rodar o setup do RAG
Confirme que há arquivos `.pdf` dentro de `data/pdfs/` antes de executar `python -m kb.setup_rag`.

### Erro de permissão ao ativar o venv no PowerShell (Windows)
Execute o PowerShell como Administrador e rode:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```
