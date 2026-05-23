# Semana 1 S1-01: Definir contrato oficial de pergunta e resposta do assistente 
Feito com Gemini modelo pro

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

---

# Implementar todas as Tasks da semana 2 do backlog de 5 semanas
Feito com codex(revisão automatica, gpt5.5 com pensamento alto e o modo de incluir contexto de arquivos abertos e ide)

## prompt 1

Quero que crie uma branch nova chamada dev-vinicius-semana-2 a partir da main, analise backlog_5_semanas_objetivos.md e faça todas as tarefas da semana 2 que são: # Semana 2 — MVP Web funcional

Objetivo da semana

Transformar a busca semântica inicial em uma experiência real de uso pela Web, com resposta gerada por IA e controle de fallback.

Resultado esperado

Ao final da semana, o usuário deve conseguir conversar com o assistente pela interface Web, receber resposta baseada na documentação, avaliar a resposta e ter o histórico salvo.

---

Tarefas da Semana 2

| Código | Nome da tarefa | Objetivo |
|---|---|---|
| S2-01 | Integrar LLM ao endpoint /ask | Permitir que o sistema gere uma resposta em linguagem natural a partir do contexto recuperado no Qdrant. |
| S2-02 | Criar prompt base com regras de resposta | Definir tom, formato, restrições de uso da base, comportamento contra alucinação e padrão de fallback. |
| S2-03 | Implementar resposta baseada exclusivamente no contexto | Garantir que o assistente responda apenas quando houver informação suficiente nos documentos recuperados. |
| S2-04 | Implementar fallback para ausência de contexto confiável | Fazer o assistente informar que não encontrou base suficiente quando a pergunta não puder ser respondida com segurança. |
| S2-05 | Definir score mínimo de relevância do Qdrant | Estabelecer um limite técnico para decidir se o contexto recuperado é confiável o suficiente para gerar resposta. |
| S2-06 | Persistir pergunta, resposta, score e fontes no MySQL | Garantir rastreabilidade, auditoria e análise futura das interações realizadas com o assistente. |
| S2-07 | Criar tela de chat Web | Disponibilizar uma interface simples para o usuário enviar perguntas e visualizar respostas. |
| S2-08 | Integrar tela Web ao endpoint /ask | Fechar o fluxo Web → API → IA/RAG → resposta ao usuário. |
| S2-09 | Implementar loading e renderização de mensagens | Melhorar a experiência de uso durante o processamento das respostas. |
| S2-10 | Criar botão de feedback útil/não útil | Permitir que o usuário avalie a qualidade da resposta recebida. |
| S2-11 | Persistir feedback vinculado à resposta | Relacionar cada avaliação do usuário à resposta gerada, permitindo análise de qualidade. |
| S2-12 | Criar testes de pergunta conhecida e pergunta fora da base | Validar os dois cenários mais importantes da POC: resposta correta e fallback seguro. |

Critério de pronto da Semana 2

text
Usuário pergunta pela Web
→ sistema busca contexto no Qdrant
→ LLM responde com base na documentação
→ histórico é salvo
→ usuário avalia a resposta
→ fallback funciona quando não há base suficiente


Marco da Semana 2

Ao final da Semana 2, o projeto deve possuir o **MVP técnico Web**.

## prompt 2 

[tsconfig.json](AssistAI/frontend/tsconfig.json) está com erro na linha 13

## prompt 3

Rode todos os testes necessarios e relevantes para os arquivos que foi editados para validar que estaja sem problemas

resposta: 

Validei os arquivos alterados e encontrei um problema real no caminho Qdrant: a pergunta conhecida "Como abrir chamado no suporte?" obtinha score 0.3198, abaixo do limite 0.35, causando fallback no perfil Docker.

Corrigi a indexação para incorporar título e categoria ao vetor do chunk em qdrant.py (line 39), elevando o score da pergunta conhecida para 0.3592. Também adicionei o teste de regressão em test_qdrant_retriever.py (line 6).

Validações executadas
- Backend: python -m pytest -p no:cacheprovider tests
Resultado: 8 passed.
- Backend lint: python -m ruff check app tests
Resultado: aprovado.
- Frontend: npm run build
Resultado: TypeScript e build Vite aprovados.
- Docker Compose: docker compose config --quiet
Resultado: configuração válida.
- Integração real com containers descartáveis MySQL + Qdrant:pergunta conhecida respondida com contexto e score 0.3592;
 - pergunta fora da base retornou fallback;
 - histórico persistiu 2 mensagens;
 - feedback foi persistido.

- Containers temporários encerrados e removidos após o teste.
- git diff --check: sem erros de whitespace.
---