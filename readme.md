# AssistAI — Assistente de Atendimento Inteligente

**Branch:** `dev-kelven`
**Versão:** 0.1.0
**Stack:** Python 3.11+ · FastAPI · React 18 · TypeScript · MySQL 8.4 · Qdrant · LangGraph · OpenAI/Ollama

---

AssistAI é uma plataforma de assistente virtual com RAG semântico, multicanal (Web + Telegram), orquestração por LangGraph, e persistência híbrida (memória/MySQL). Construída com Clean Architecture e DDD leve para máxima extensibilidade.

## Funcionalidades Principais

- **RAG Semântico** — Busca vetorial em Qdrant com embeddings OpenAI ou Ollama
- **Multicanal** — Web (React) e Telegram compartilhando o mesmo motor de IA
- **LangGraph** — Fluxo de decisão multiagente com 11 nós especializados
- **LLM Multi-Provider** — OpenAI e Ollama (local) com fallback automático
- **Persistência Híbrida** — In-memory para desenvolvimento, MySQL para produção
- **Fallback Inteligente** — Escalonamento humano quando não há base suficiente
- **Métricas e Feedback** — Taxa de fallback, acurácia, documentos mais usados
- **MCP Simulado** — Ferramenta externa simulada para consulta de chamados

## Stack Técnica

| Camada | Tecnologia |
|---|---|
| Backend | Python 3.11+, FastAPI, Uvicorn |
| Frontend | React 18, TypeScript, Vite 6, Lucide Icons |
| Banco Relacional | MySQL 8.4 (SQLAlchemy 2.0) |
| Banco Vetorial | Qdrant 1.11 |
| Orquestração | LangGraph 1.2 |
| LLM Providers | OpenAI API, Ollama (local) |
| Embeddings | OpenAI text-embedding-3-small, Ollama nomic-embed-text |
| Testes | Pytest 9, pytest-cov, HTTPX |
| Linter | Ruff |
| Qualidade | SonarQube |

## Primeiros Passos Rápidos

```bash
# Ambiente virtual + dependências
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev,ai,database]"

# Executar (modo memória + LLM mock — sem dependências externas)
uvicorn app.main:app --reload

# Testar
python -m pytest tests/ -v
```

## Documentação Detalhada

A documentação completa do projeto está em `docs/`:

| Documento | Conteúdo |
|---|---|
| [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) | Decisões arquiteturais, camadas, fluxos, tradeoffs |
| [`docs/API.md`](docs/API.md) | Endpoints, payloads, respostas, exemplos |
| [`docs/RAG.md`](docs/RAG.md) | Pipeline RAG, embeddings, Qdrant, anti-alucinação |
| [`docs/CHANGELOG.md`](docs/CHANGELOG.md) | Histórico técnico de implementações |
| [`docs/setup_local.md`](docs/setup_local.md) | Setup completo local |
| [`docs/estrutura_projeto.md`](docs/estrutura_projeto.md) | Estrutura de diretórios |
| [`docs/backlog_5_semanas_objetivos.md`](docs/backlog_5_semanas_objetivos.md) | Backlog original do projeto |

---

## Licença

Eclipse Public License v2.0
