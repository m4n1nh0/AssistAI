# Estrutura base do projeto

```text
AssistAI/
  backend/                 API FastAPI, casos de uso, dominio e adaptadores
  frontend/                Aplicacao React + TypeScript
  infra/                   Scripts e configuracoes de infraestrutura local
  knowledge_base/          Conteudos iniciais para validacao do RAG
  docs/                    Documentacao de arquitetura, backlog e apoio ao time
  docker-compose.yml       MySQL, Qdrant, backend e frontend locais
```

## Principios usados

- Monorepo simples para facilitar a POC de 5 semanas.
- Backend em camadas pragmaticas: API, application, domain e infrastructure.
- Frontend separado em presentation, application, domain, infrastructure e shared.
- Dependencias externas iniciam como adaptadores substituiveis.
- Fluxo principal demonstravel desde a primeira semana: pergunta, busca, resposta, historico e feedback.

