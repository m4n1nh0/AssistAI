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

```powershell
docker compose up -d mysql qdrant
```

## Validacao

```powershell
cd backend
.\.venv\Scripts\python -m pytest tests
.\.venv\Scripts\python -m ruff check .

cd ..\frontend
npm run build
```

