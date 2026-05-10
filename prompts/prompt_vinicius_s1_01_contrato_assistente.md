## Prompt 1 — Solicitação inicial da task

Quero fazer essa task | S1-01 | Definir contrato oficial de pergunta e resposta do assistente | Padronizar a comunicação entre Web, Telegram, API e motor de IA, evitando retrabalho entre as frentes de desenvolvimento. |

## Prompt 2 — Validação do que faltava após adicionar os códigos

coloquei na ide os codigos gerados por voce dos temas abaixo:
6. Modelos Pydantic
7. Exemplo de endpoint FastAPI
8. Testes iniciais de contrato
9. Documento para colocar em docs

além desses o que falta e onde colocar cada um?

## Prompt 3 — Análise da arquitetura real do projeto

O app/main.py está assim e a arquitetura está anexada
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.application.services.assistant_service import AssistantService
from app.application.services.document_service import DocumentService
from app.application.services.feedback_service import FeedbackService
from app.application.services.metrics_service import MetricsService
from app.application.services.telegram_service import TelegramService
from app.core.config import get_settings
from app.core.logging import configure_logging
from app.infrastructure.llm.fake_llm import FakeLLMGateway
from app.infrastructure.mcp.simulated_tools import SimulatedToolRegistry
from app.infrastructure.rag.simple_retriever import SimpleRetriever
from app.infrastructure.repositories.memory import InMemoryRepository

app.include_router(api_router, prefix=settings.api_prefix)

## Prompt 4 — Instalação das dependências com `pyproject.toml`

tenho o pyproject.toml como instalo as dependencias

## Prompt 5 — Primeiro erro nos testes e no Ruff

(.venv) PS C:\desafios_eng_prompt\AssistAI\backend> .\.venv\Scripts\python -m pytest tests
...
tests\test_assistant_contract.py F..
...
assert response.status_code == 200
E assert 422 == 200

(.venv) PS C:\desafios_eng_prompt\AssistAI\backend> .\.venv\Scripts\python -m ruff check .
...
Import block is un-sorted or un-formatted
Line too long


## Prompt 6 — Segundo erro: contrato antigo versus contrato novo

(.venv) PS C:\desafios_eng_prompt\AssistAI\backend> .\.venv\Scripts\python -m pytest tests
...
tests\test_api_contracts.py .FFF
...
response = client.post(
    "/ask",
    json={
        "user_id": "web-user-001",
        "channel": "web",
        "message": "Como abrir chamado no suporte?",
    },
)
...
assert response.status_code == 200
E assert 422 == 200

## Prompt 7 — Terceiro erro: campo `fallback` removido

(.venv) PS C:\desafios_eng_prompt\AssistAI\backend> .\.venv\Scripts\python -m pytest tests
...
assert body["fallback"] is False
KeyError: 'fallback'
...
assert body["fallback"] is True
KeyError: 'fallback'
...
assert response.status_code == 200
E assert 404 == 200


## Prompt 8 — Ajuste da documentação do contrato

ajuste a documentação de contrato_assistente com as alterações feitas no formato .md faça no mesmo modo de um codigo executavel


## Prompt 9 — Versão final mais objetiva da documentação

refaça só com os pontos fundamentais extendendo o conteudo original:
Contrato oficial do assistente
Endpoint
POST /ask
Objetivo
Padronizar a comunicação entre Web, Telegram, API e motor de IA/RAG.

adicionando as mudanças a serem documentadas

## Prompt 10 — Documentação de prompts

gostaria de um arquivo mostrando os prompts que enviei para gerar o codigo funcional. me traga eles para documentação

## Resumo dos prompts e decisões geradas

| Prompt   | Principal decisão gerada |
|----------|--------------------------|
| Prompt 1 | Criar contrato oficial do `/ask`. |
| Prompt 2 | Identificar arquivos restantes e pontos de integração. |
| Prompt 3 | Registrar rota no `app/api/router.py`, não diretamente no `main.py`. |
| Prompt 4 | Criar venv e instalar dependências com `pip install -e ".[dev]"`. |
| Prompt 5 | Resolver conflito entre `ask.py` e `assistant.py`. |
| Prompt 6 | Atualizar testes antigos de `message` para `question`. |
| Prompt 7 | Trocar `fallback` por `status` nos testes e documentação. |
| Prompt 8 | Atualizar documentação completa do contrato. |
| Prompt 9 | Gerar versão final objetiva da documentação. |
| Prompt 10| Gerar documentação de prompts. |
