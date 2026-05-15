# Setup local

## Pre-requisitos

- Docker Engine e Docker Compose v2;
- Node.js e Python apenas se quiser rodar frontend/backend fora de containers.

## Configuracao inicial

Copie o arquivo de exemplo de variáveis para um `.env` local quando for executar serviços fora do Docker:

```bash
cp .env.example .env
```

## Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

## Frontend

```bash
cd frontend
npm install
export VITE_API_URL="http://localhost:8000"
npm run dev
```

## Infraestrutura local

```bash
docker compose up -d mysql qdrant
docker compose ps
docker compose logs -f mysql qdrant
```

## Validacao

```bash
cd backend
source .venv/bin/activate
python -m pytest tests
python -m ruff check .

cd ../frontend
npm run build
```

