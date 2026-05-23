# Setup local

## Backend

### Windows PowerShell

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\python -m pip install -e ".[dev]"
.\.venv\Scripts\python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

### Linux / macOS

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

### WSL

Use WSL2 para suporte a Docker. Se o comando `docker` não existir, instale o Docker Desktop e habilite a integração WSL.

## Frontend

### Windows PowerShell

```powershell
cd frontend
npm install
$env:VITE_API_URL = "http://localhost:8000"
npm run dev
```

### Linux / macOS

```bash
cd frontend
npm install
export VITE_API_URL="http://localhost:8000"
npm run dev -- --host 0.0.0.0
```

### Observação

Se o Node falhar com `Exec format error` ou outros erros de binário, o ambiente local pode estar configurado com uma arquitetura incompatível. Use Docker ou instale uma versão compatível do Node.js.

## Infraestrutura local

```bash
docker compose up -d mysql qdrant
```

## Validacao

### Backend

```bash
cd backend
source .venv/bin/activate
python -m pytest tests
python -m ruff check .
```

### Frontend

```bash
cd frontend
npm run build
```

