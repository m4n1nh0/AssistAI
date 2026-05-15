# Assistente de Atendimento Inteligente

POC de assistente de suporte interno com Web Chat, FastAPI, RAG inicial, fallback, feedback, Telegram webhook simulado, MCP simulado, MySQL e Qdrant preparados em containers.

## Estrutura

```text
atendimento-inteligente/
  backend/
    app/
      api/              rotas e schemas FastAPI
      application/      casos de uso
      ai/               intencao, RAG simples e gateway LLM mock
      domain/           modelos de negocio
      infrastructure/   repositorio em memoria e MCP simulado
      core/             configuracoes
    tests/
  frontend/
    src/
      components/
      services/
      domain/
  docs/
  docker-compose.yml
```

## Como rodar

Suba MySQL e Qdrant:

```bash
docker compose up -d
```

Backend:

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

URLs:

- Web: `http://localhost:5173`
- Swagger: `http://localhost:8000/docs`
- Health: `http://localhost:8000/health`
- Qdrant: `http://localhost:6333/dashboard`

## Endpoints principais

- `POST /api/ask`
- `POST /api/feedback`
- `GET /api/attendances`
- `GET /api/attendances/{attendance_id}`
- `GET /api/documents`
- `POST /api/documents`
- `POST /api/documents/reindex`
- `POST /api/telegram/webhook`

## Observacao

Esta base foi montada para POC. O RAG e o LLM estao em modo mock/in-memory para permitir demonstracao imediata sem chave externa. A evolucao natural e trocar `SimpleRetriever` por Qdrant real, `MockLLMGateway` por um provedor de LLM e `InMemoryRepository` por MySQL.
