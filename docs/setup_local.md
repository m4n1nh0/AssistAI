# Setup local

## Backend

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\python -m pip install -e ".[dev]"
.\.venv\Scripts\python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

## Frontend

```powershell
cd frontend
npm install
$env:VITE_API_URL = "http://localhost:8000"
npm run dev
```

## Infraestrutura local

MySQL e Qdrant rodam via Docker Compose para manter o ambiente de
persistencia transacional e busca vetorial igual entre os devs.

Pre-requisito: Docker Desktop/engine em execucao.

```powershell
docker compose up -d mysql qdrant
```

Credenciais e endpoints locais:

| Servico | Uso local |
|---|---|
| MySQL | `mysql+pymysql://assistai:assistai@localhost:3306/assistai` |
| Qdrant HTTP | `http://localhost:6333` |
| Qdrant gRPC | `localhost:6334` |
| Collection padrao | `assistai_knowledge` |

O schema inicial do MySQL fica em `infra/mysql/init/001_schema.sql` e roda
automaticamente na primeira criacao do volume `mysql_data`.

Para validar os servicos:

```powershell
docker compose ps mysql qdrant
docker compose exec mysql mysql -uassistai -passistai assistai -e "SHOW TABLES;"
Invoke-RestMethod http://localhost:6333/healthz
```

Para parar mantendo os dados:

```powershell
docker compose stop mysql qdrant
```

Para recriar o ambiente do zero, removendo os volumes locais:

```powershell
docker compose down -v
docker compose up -d mysql qdrant
```

## Indexacao da base

Com MySQL, Qdrant e backend em execucao, reindexe a base inicial:

```powershell
Invoke-RestMethod -Method Post http://localhost:8000/documents/reindex
```

## Validacao

```powershell
cd backend
.\.venv\Scripts\python -m pytest tests
.\.venv\Scripts\python -m ruff check .

cd ..\frontend
npm run build
```
