# Backend FastAPI

Estrutura inicial da API central do AssistAI, criada para receber mensagens dos
canais Web e Telegram, acionar os servicos de aplicacao e manter pontos claros
de evolucao para IA/RAG, MySQL e Qdrant.

## Como executar localmente

```powershell
cd backend
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Endpoints de apoio:

- `GET /health`: verificacao simples da API.
- `GET /docs`: documentacao interativa do FastAPI.
- `GET /openapi.json`: contrato executavel da API.

## Camadas

| Caminho | Responsabilidade |
|---|---|
| `app/main.py` | Cria a aplicacao FastAPI, configura CORS e compoe dependencias iniciais. |
| `app/api` | Rotas HTTP, router central e dependencias de injecao. |
| `app/application/services` | Casos de uso: assistente, documentos, feedback, metricas e Telegram. |
| `app/domain` | Contratos Pydantic, enums e modelos de dominio. |
| `app/infrastructure/repositories` | Adaptador inicial em memoria para acelerar a POC. |
| `app/infrastructure/rag` | Recuperador inicial usado antes da integracao completa com Qdrant. |
| `app/infrastructure/database` | Ponto de extensao para persistencia MySQL. |
| `app/infrastructure/vector` | Ponto de extensao para Qdrant. |
| `app/infrastructure/llm` | Gateway inicial de LLM mockado. |
| `tests` | Testes de contrato e bootstrap da API. |

## Bootstrap atual

`create_app()` instancia e registra em `app.state`:

- repositorio em memoria com documentos de suporte iniciais;
- `MySqlUnitOfWork`, configurado por `ASSISTAI_MYSQL_URL`;
- `QdrantVectorStore`, configurado por `ASSISTAI_QDRANT_URL` e
  `ASSISTAI_QDRANT_COLLECTION`;
- recuperador RAG inicial;
- gateway LLM fake;
- registry MCP simulado;
- servicos de aplicacao usados pelas rotas.

## Rotas iniciais

| Rota | Objetivo |
|---|---|
| `POST /ask` | Receber pergunta e retornar resposta do assistente. |
| `POST /telegram/webhook` | Receber mensagem Telegram e reutilizar o fluxo do assistente. |
| `POST /feedback` | Registrar avaliacao de resposta. |
| `GET /attendances` | Listar atendimentos. |
| `GET /attendances/{attendance_id}` | Detalhar mensagens de um atendimento. |
| `GET /documents` | Listar documentos da base. |
| `POST /documents` | Cadastrar documento. |
| `POST /documents/reindex` | Reindexar documentos. |
| `GET /metrics` | Expor indicadores basicos. |

## Variaveis principais

As configuracoes usam prefixo `ASSISTAI_` e podem ser declaradas em `.env`.
Consulte `.env.example` na raiz do projeto para valores locais.
