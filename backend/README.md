# AssistAI Backend

Este é o backend do projeto AssistAI, construído com **FastAPI**.

## Estrutura do Projeto

O projeto segue os princípios da **Clean Architecture**:

- `app/api/`: Rotas e definições de endpoints da API.
- `app/application/`: Serviços de aplicação e lógica de negócio de alto nível.
- `app/core/`: Configurações globais, logging e utilitários centrais.
- `app/domain/`: Modelos de domínio, entidades e contratos (interfaces).
- `app/infrastructure/`: Implementações concretas de infraestrutura (Banco de Dados, Banco Vetorial, LLMs, Telegram).

## Tecnologias e Integrações

- **Banco Relacional (MySQL)**: Integrado via SQLAlchemy. A base está configurada em `app/infrastructure/database/`.
- **Banco Vetorial (Qdrant)**: Preparado para busca semântica em `app/infrastructure/vector/`.
- **IA/LLM**: Abstração preparada para integração com diferentes provedores (OpenAI, mock, etc) em `app/infrastructure/llm/`.
- **Telegram**: Integração via Webhook preparada em `app/infrastructure/telegram/`.

## Configuração

O backend utiliza variáveis de ambiente para configuração. Veja `app/core/config.py` para as opções disponíveis.
Você pode configurar as seguintes flags para alternar entre mocks e implementações reais:

- `ASSISTAI_USE_REAL_DATABASE=true/false`
- `ASSISTAI_USE_REAL_VECTOR_STORE=true/false`
- `ASSISTAI_LLM_PROVIDER=mock/openai/...`

## Como Executar

1. Crie um ambiente virtual: `python -m venv venv`
2. Ative o ambiente: `source venv/bin/activate` (ou `venv\Scripts\activate` no Windows)
3. Instale as dependências: `pip install -e ".[dev,database,ai]"`
4. Execute a aplicação: `uvicorn app.main:app --reload`
