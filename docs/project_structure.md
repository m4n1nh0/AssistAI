# Estrutura base do projeto

```text
backend/
  app/
    api/                 Rotas FastAPI e contratos HTTP
    application/         Servicos de aplicacao e casos de uso
    core/                Configuracoes e logging
    db/                  Espaco reservado para MySQL, ORM e migrations
    domain/              Entidades e enums do dominio
    graph/               Espaco reservado para LangGraph
    infrastructure/      Adaptadores de LLM, Qdrant, Telegram, MCP e repositorios
    jobs/                Rotinas operacionais, como reindexacao
    observability/       Metricas e medicao de duracao
    rag/                 Loader, chunking, recuperacao, prompt e intencao
    schemas/             Schemas Pydantic da API
    security/            Sanitizacao e protecao basica contra prompt injection
  tests/                 Testes de contrato e regressao

frontend/
  src/
    application/         Hooks e estado de tela
    domain/              Tipos compartilhados da interface
    infrastructure/      Cliente HTTP da API
    presentation/        Layout, navegacao, telas e componentes

docs/
  knowledge_base/        Base inicial de suporte interno para o RAG
  api_contracts.md       Contratos iniciais dos endpoints
  setup_local.md         Como rodar backend, frontend e Docker

docker-compose.yml       MySQL, Qdrant, backend e frontend
```

## Fatias ja preparadas

- `/ask` com contrato funcional e busca local na base de conhecimento.
- `/feedback`, `/attendances`, `/documents`, `/documents/reindex`, `/metrics` e `/telegram/webhook`.
- Frontend com Chat, Historico, Documentos e Indicadores.
- Tela de Documentos com cadastro manual, listagem e reindexacao.
- Base de conhecimento inicial com abertura de chamado, reset de senha e atendimento humano.
- Dockerfiles e `docker-compose.yml` para ambiente reproduzivel.
- Testes de contrato cobrindo ask, fallback, prompt injection, documentos, metricas e Telegram.

## Proximas implementacoes naturais

- Persistencia real com SQLAlchemy/Alembic em MySQL.
- Indexacao real de embeddings no Qdrant.
- Gateway real de LLM com prompt controlado.
- LangGraph na camada `backend/app/graph`.
- Upload de documentos e ativacao/inativacao pela interface.
- Testes de integracao com MySQL, Qdrant e Telegram simulado.
