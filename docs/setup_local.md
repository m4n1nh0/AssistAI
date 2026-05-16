# Setup local

## Requisitos

- Python 3.12+
- Node.js 22+
- Docker Desktop

## Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

API: `http://localhost:8000`

Swagger: `http://localhost:8000/docs`

## Frontend

```bash
cd frontend
npm install
npm run dev
```

Web: `http://localhost:5173`

## Ambiente completo com Docker

```bash
docker compose up --build
```

Servicos:

- Backend: `http://localhost:8000`
- Frontend: `http://localhost:5173`
- MySQL: `localhost:3306`
- Qdrant: `http://localhost:6333`

## Fluxo inicial validado

```text
Web Chat
-> POST /ask
-> busca local na base docs/knowledge_base
-> resposta com fonte ou fallback
-> historico em memoria
-> feedback em memoria
-> cadastro manual de documentos pela tela Documentos
-> reindexacao simulada pela API
```

Persistencia real em MySQL e indexacao real no Qdrant ficam como proxima fatia de implementacao.
