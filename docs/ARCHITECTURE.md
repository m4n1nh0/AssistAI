# Arquitetura — AssistAI

> **Branch:** `dev-kelven` | **Versão:** 0.1.0
> Documento de arquitetura de software — decisões, camadas, fluxos e tradeoffs.

---

## Índice

1. [Visão Geral](#1-visão-geral)
2. [Clean Architecture](#2-clean-architecture)
3. [Camadas Detalhadas](#3-camadas-detalhadas)
4. [Fluxo da Aplicação](#4-fluxo-da-aplicação)
5. [Fluxo LangGraph](#5-fluxo-langgraph)
6. [Estratégia de Persistência](#6-estratégia-de-persistência)
7. [Estratégia Multi-Provider](#7-estratégia-multi-provider)
8. [Estratégia de Desacoplamento](#8-estratégia-de-desacoplamento)
9. [Tradeoffs e Decisões](#9-tradeoffs-e-decisões)

---

## 1. Visão Geral

O AssistAI é construído sobre **Clean Architecture** com **DDD leve**, onde o domínio é o centro do sistema e as camadas externas (infraestrutura, API, serviços) dependem dele, nunca o contrário.

```
┌─────────────────────────────────────────────────────┐
│                    API Layer                         │
│              (FastAPI routes + DI)                    │
├─────────────────────────────────────────────────────┤
│                Application Layer                      │
│          (Services, orquestração)                     │
├─────────────────────────────────────────────────────┤
│                  Domain Layer                         │
│     (Entidades, enums, protocols, contracts)         │
├─────────────────────────────────────────────────────┤
│              Infrastructure Layer                     │
│  (MySQL, Qdrant, LLM, LangGraph, Embeddings, ...)    │
└─────────────────────────────────────────────────────┘
```

### Princípios

- **Domínio puro** — Sem dependências de frameworks ou bibliotecas externas
- **Inversão de dependência** — Infraestrutura implementa interfaces definidas no domínio
- **Injeção de dependência** — FastAPI `Depends` + construtores explícitos
- **Protocolos, não classes concretas** — Acoplamento mínimo via ABCs

---

## 2. Clean Architecture

### Regra de Dependência

As setas de dependência apontam **para dentro**:

```
API → Application → Domain
Infrastructure → Domain
```

Nenhuma camada interna conhece a externa. O domínio não importa FastAPI, SQLAlchemy, Qdrant ou OpenAI.

### Protocolos de Domínio

Definidos em `app/domain/protocols.py`:

| Protocolo | Responsabilidade | Implementações |
|---|---|---|
| `LLMGateway` | Geração de texto via LLM | `FakeLLMGateway`, `OpenAILLMGateway`, `OllamaLLMGateway` |
| `Retriever` | Busca de contexto relevante | `SimpleRetriever`, `SemanticRetriever` |
| `Repository` | Persistência de dados | `InMemoryRepository`, `MySqlRepository` |
| `EmbeddingService` | Geração de embeddings | `OpenAIEmbeddingService`, `OllamaEmbeddingService`, `MockEmbeddingService` |

---

## 3. Camadas Detalhadas

### 3.1 Domain Layer (`backend/app/domain/`)

Núcleo do sistema, **sem dependências externas**.

```
domain/
├── contracts.py    → Schemas Pydantic (AskRequest, AskResponse, etc.)
├── enums.py        → Channel, DocumentStatus, Intent
├── models.py       → Dataclasses (User, Attendance, MessageRecord, etc.)
└── protocols.py    → ABCs (LLMGateway, Retriever, Repository, EmbeddingService)
```

**Entidades principais:**

- `User` — Usuário do sistema (Web ou Telegram)
- `Attendance` — Sessão de atendimento
- `MessageRecord` — Mensagem trocada (pergunta + resposta)
- `KnowledgeDocument` — Documento da base de conhecimento
- `DocumentChunk` — Fragmento de documento indexado
- `Feedback` — Avaliação do usuário sobre a resposta
- `AiLog` — Log de execução do motor de IA

### 3.2 Application Layer (`backend/app/application/`)

Orquestração dos casos de uso. Depende do domínio e da infraestrutura via injeção.

```
application/services/
├── assistant_service.py   → Ponto de entrada do assistente
├── document_service.py    → CRUD de documentos
├── feedback_service.py    → Registro de feedback
├── metrics_service.py     → Métricas operacionais
└── telegram_service.py    → Handler do Telegram
```

O `AssistantService` é o orquestrador principal. Ele instancia o `AssistantGraph` (LangGraph) e delega a execução para ele.

### 3.3 API Layer (`backend/app/api/`)

Interface HTTP com FastAPI. Contém routes, dependencies e o router principal.

```
api/
├── router.py          → Agrega todos os routers
├── dependencies.py    → Injeção de dependência via FastAPI Depends
└── routes/
    ├── ask.py         → POST /ask
    ├── feedback.py    → POST /feedback
    ├── attendances.py → GET /attendances, GET /attendances/{id}
    ├── documents.py   → GET/POST /documents, POST /documents/reindex
    ├── metrics.py     → GET /metrics
    ├── health.py      → GET /health
    └── telegram.py    → POST /telegram/webhook
```

### 3.4 Infrastructure Layer (`backend/app/infrastructure/`)

Implementações concretas dos protocolos de domínio.

```
infrastructure/
├── database/        → MySQL (SQLAlchemy models + MySqlRepository)
├── embeddings/      → OpenAI, Ollama, Mock (factory)
├── graph/           → LangGraph (AssistantGraph com 11 nós)
├── llm/             → OpenAI, Ollama, Fake
├── mcp/             → Ferramentas simuladas (ticket_status)
├── prompts/         → Templates de prompt do sistema
├── rag/             → SimpleRetriever, SemanticRetriever
├── repositories/    → InMemoryRepository
├── telegram/        → Telegram client (stub)
└── vector/          → QdrantVectorStore
```

---

## 4. Fluxo da Aplicação

### 4.1 Fluxo Principal (LangGraph)

```
Usuário → POST /ask → AssistantService.ask() → AssistantGraph.run()
                                                      │
                                         ┌────────────▼────────────┐
                                         │       sanitize           │
                                         │  (normaliza mensagem)   │
                                         └────────────┬────────────┘
                                                      │
                                         ┌────────────▼────────────┐
                                         │       classify          │
                                         │  (detecta intenção)     │
                                         └────────────┬────────────┘
                                                      │
                                         ┌────────────▼────────────┐
                                         │      setup_user         │
                                         │  (find or create)       │
                                         └────────────┬────────────┘
                                                      │
                                         ┌────────────▼────────────┐
                                         │    setup_attendance     │
                                         │  (cria sessão)          │
                                         └────────────┬────────────┘
                                                      │
                                         ┌────────────▼────────────┐
                                         │       retrieve          │
                                         │  (busca contexto RAG)   │
                                         └────────────┬────────────┘
                                                      │
                                         ┌────────────▼────────────┐
                                         │        filter           │
                                         │  (filtra por score)     │
                                         └────────────┬────────────┘
                                                      │
                                         ┌────────────▼────────────┐
                                         │     route (condicional) │
                                         └────────────┬────────────┘
                                                      │
              ┌─────────────────┬──────────┬──────────┼──────────┬──────────┐
              ▼                 ▼          ▼          ▼          ▼          ▼
         greeting       human_request  ticket   has_context  no_context
         (saudação)     (escalona)   (chamado)  (gera LLM)  (fallback)
              │                 │          │          │          │
              └─────────────────┴──────────┴──────────┴──────────┘
                                                      │
                                         ┌────────────▼────────────┐
                                         │        persist          │
                                         │  (salva msg + log)      │
                                         └────────────┬────────────┘
                                                      │
                                              ┌───────▼───────┐
                                              │  AskResponse  │
                                              └───────────────┘
```

### 4.2 Fluxo Manual (Fallback)

O `AssistantService` mantém o método `ask_procedural()` como fallback, que executa o mesmo fluxo sem LangGraph, na forma procedural original.

---

## 5. Fluxo LangGraph

### 5.1 Estado Compartilhado

```python
class GraphState(TypedDict):
    user_message: str          # Input original
    user_id: str               # ID do usuário
    channel: str               # Canal (web/telegram)
    sanitized_message: str     # Mensagem normalizada
    intent: str                # Intenção classificada
    confidence: float          # Score de confiança
    fallback: bool             # Flag de fallback
    answer: str                # Resposta gerada
    sources: list[dict]        # Fontes utilizadas
    user: object               # User domain object
    attendance: object         # Attendance domain object
    contexts: list             # Contextos recuperados
    message_record: object     # MessageRecord persistido
```

### 5.2 Nós do Grafo

| Nó | Função | Responsabilidade |
|---|---|---|
| `sanitize` | `_sanitize` | Normaliza espaços, limpa entrada |
| `classify` | `_classify` | Classifica intenção (regex) |
| `setup_user` | `_setup_user` | Busca/cria usuário no repositório |
| `setup_attendance` | `_setup_attendance` | Cria sessão de atendimento |
| `retrieve` | `_retrieve` | Busca contexto no retriever |
| `filter` | `_filter` | Filtra por score mínimo de relevância |
| `router` | `_router` | Roteia condicionalmente baseado na intenção |
| `greeting` | `_respond_greeting` | Responde saudação |
| `human_request` | `_respond_human` | Escalona para humano |
| `ticket` | `_respond_ticket` | Consulta status de chamado |
| `has_context` | `_generate_with_context` | Gera resposta via LLM |
| `no_context` | `_respond_fallback` | Retorna fallback |
| `persist` | `_persist` | Persiste mensagem e log |

### 5.3 Roteamento Condicional

O nó `filter` possui arestas condicionais baseadas no valor de `intent`:

| Intenção | Rota |
|---|---|
| `saudacao` | → `greeting` |
| `solicitacao_humana` | → `human_request` |
| `consulta_chamado` | → `ticket` |
| `procedimento` (com contexto) | → `has_context` |
| `procedimento` (sem contexto) | → `no_context` |

---

## 6. Estratégia de Persistência

### 6.1 Repositório Abstrato

O protocolo `Repository` (18 métodos) abstrai toda persistência. As implementações:

| Implementação | Uso | Características |
|---|---|---|
| `InMemoryRepository` | Desenvolvimento / Testes | Thread-safe com RLock, sem dependências |
| `MySqlRepository` | Produção | SQLAlchemy 2.0, transações, pool |

### 6.2 Chaveamento por Config

```python
ASSISTAI_DATABASE_PERSISTENCE=memory   # → InMemoryRepository
ASSISTAI_DATABASE_PERSISTENCE=mysql    # → MySqlRepository
```

### 6.3 MySQL — Modelos

8 tabelas mapeadas com SQLAlchemy 2.0 Declarative:

| Tabela | PK | Descrição |
|---|---|---|
| `users` | `id` | Usuários dos canais |
| `attendances` | `id` | Sessões de atendimento |
| `messages` | `id` | Mensagens trocadas |
| `documents` | `id` | Documentos da base de conhecimento |
| `document_chunks` | `id` | Chunks dos documentos |
| `feedbacks` | `id` | Avaliações dos usuários |
| `ai_logs` | `id` | Logs de execução da IA |
| `handoffs` | `id` | Escalonamentos para humano |
| `tool_calls` | `id` | Chamadas de ferramentas MCP |

### 6.4 Unit of Work

`MySqlUnitOfWork` gerencia ciclo de vida da engine e session factory SQLAlchemy. Criado em `main.py` e injetado no `MySqlRepository`.

---

## 7. Estratégia Multi-Provider

### 7.1 LLM

Chaveamento via `ASSISTAI_LLM_PROVIDER`:

| Provider | Classe | Requer |
|---|---|---|
| `mock` | `FakeLLMGateway` | Nada (retorna primeiro chunk) |
| `openai` | `OpenAILLMGateway` | `ASSISTAI_LLM_API_KEY` |
| `ollama` | `OllamaLLMGateway` | Ollama rodando localmente |

**Padrão de resiliência:** Retry (2 tentativas), timeout configurável, captura de `RateLimitError`, `APITimeoutError`, `APIError` com fallback amigável.

### 7.2 Embeddings

Chaveamento via `ASSISTAI_EMBEDDING_PROVIDER` (fallback para `ASSISTAI_LLM_PROVIDER`):

| Provider | Classe | Requer |
|---|---|---|
| `openai` | `OpenAIEmbeddingService` | `ASSISTAI_EMBEDDING_API_KEY` |
| `ollama` | `OllamaEmbeddingService` | Ollama rodando com modelo de embedding |

Se nenhum provider for configurado, `MockEmbeddingService` retorna vetor de zeros para desenvolvimento.

---

## 8. Estratégia de Desacoplamento

### 8.1 Injeção de Dependência

Todas as dependências são injetadas via construtor. O `main.py` funciona como **Composition Root**, onde todas as instâncias são criadas e conectadas.

```python
# main.py (simplificado)
repository = _build_repository(settings)
retriever, vector_store = _build_retriever(repository, settings)
llm_gateway = _build_llm_gateway(settings)

assistant_service = AssistantService(
    repository=repository,
    retriever=retriever,
    llm_gateway=llm_gateway,
    tools=tools,
    settings=settings,
)
```

### 8.2 Fallback Graceful

Quando uma dependência externa não está disponível:

- **Qdrant off-line** → `SemanticRetriever` falha → fallback para `SimpleRetriever` (keyword)
- **MySQL off-line** → `MySqlRepository` falha → fallback para `InMemoryRepository`
- **LLM off-line** → `OpenAILLMGateway` retorna mensagem de erro amigável

### 8.3 Testabilidade

Cada componente tem uma contraparte mock/fake para testes:

- `FakeLLMGateway` para `LLMGateway`
- `KeywordTestRetriever` para `Retriever`
- `InMemoryRepository` para `Repository`
- `MockEmbeddingService` para `EmbeddingService`

---

## 9. Tradeoffs e Decisões

### 9.1 Por que não usar um ORM completo com migrations desde o início?

**Decisão:** SQLAlchemy 2.0 com `create_all()` em vez de Alembic migrations completas.

**Motivo:** Projeto em fase de POC. `create_all()` é suficiente para desenvolvimento. Alembic está disponível como dependência opcional e pode ser adicionado quando houver múltiplos ambientes.

### 9.2 Por que LangGraph em vez de fluxo procedural?

**Decisão:** LangGraph com 11 nós substituindo o fluxo procedural original.

**Motivo:** O fluxo procedural (`ask_procedural`) foi mantido como referência, mas o LangGraph oferece:
- **Extensibilidade** — Novos nós podem ser adicionados sem modificar a lógica existente
- **Observabilidade** — Cada nó é independente e pode ser logado/monitorado
- **Preparação multicanal** — O mesmo grafo atende Web e Telegram

### 9.3 Por que manter o InMemoryRepository?

**Decisão:** `InMemoryRepository` como implementação padrão, `MySqlRepository` como opção de produção.

**Motivo:** Desenvolvedores podem rodar o projeto sem MySQL, agilizando o onboarding. O protocolo `Repository` garante que ambas as implementações sejam intercambiáveis.

### 9.4 Por que embeddings mock?

**Decisão:** `MockEmbeddingService` quando nenhum provider de embedding é configurado.

**Motivo:** Permite testar o fluxo RAG completo (chunking, busca, filtragem) sem depender de API externa ou modelo local. O vetor de zeros tem similaridade coseno = 1.0 consigo mesmo, permitindo testes determinísticos.
