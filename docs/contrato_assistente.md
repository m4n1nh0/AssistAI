# Contrato oficial de pergunta e resposta do assistente

**Tarefa:** S1-01  
**Status:** definido  
**Versao do contrato:** 1.0  
**Escopo:** Web, Telegram, API FastAPI e motor de IA/RAG

Este documento e a referencia funcional para a troca de mensagens com o
assistente. A implementacao tecnica vive em:

- Backend: `backend/app/domain/contracts.py`
- Frontend: `frontend/src/domain/contracts.ts`
- OpenAPI local: `GET /openapi.json`
- Testes de contrato: `backend/tests/test_api_contracts.py`

## Principios

- Web e Telegram devem chegar ao mesmo fluxo central do assistente.
- O endpoint `POST /ask` e o contrato canonico de pergunta e resposta.
- O Telegram pode ter payload de entrada proprio, mas deve retornar o mesmo
  `AskResponse` usado pelo Web.
- Toda resposta deve permitir rastreabilidade por `attendance_id` e
  `message_id`.
- Quando nao houver contexto confiavel, o assistente deve retornar fallback
  explicito e lista de fontes vazia.

## Entrada canonica: AskRequest

Usada por `POST /ask`.

| Campo | Tipo | Obrigatorio | Regra | Descricao |
|---|---|---:|---|---|
| `user_id` | string | sim | 1 a 128 caracteres | Identificador externo do usuario no canal de origem. |
| `channel` | enum | sim | `web` ou `telegram` | Canal que originou a pergunta. |
| `message` | string | sim | 1 a 2000 caracteres | Pergunta enviada pelo usuario em linguagem natural. |

Exemplo Web:

```json
{
  "user_id": "web-user-001",
  "channel": "web",
  "message": "Como abrir chamado no suporte?"
}
```

Exemplo Telegram normalizado para o motor:

```json
{
  "user_id": "telegram-123456",
  "channel": "telegram",
  "message": "Como resetar minha senha?"
}
```

## Saida canonica: AskResponse

Retornada por `POST /ask` e `POST /telegram/webhook`.

| Campo | Tipo | Obrigatorio | Regra | Descricao |
|---|---|---:|---|---|
| `answer` | string | sim | texto nao vazio | Resposta final que sera exibida ao usuario. |
| `fallback` | boolean | sim | `true` ou `false` | Indica se a resposta foi fallback controlado. |
| `intent` | enum | sim | ver tabela de intencoes | Intencao detectada pelo assistente. |
| `confidence` | number | sim | 0.0 a 1.0 | Confianca/relevancia usada na decisao. |
| `sources` | array | sim | pode ser vazio | Fontes usadas para fundamentar a resposta. |
| `attendance_id` | string | sim | prefixo atual `att-` | Atendimento criado ou associado a interacao. |
| `message_id` | string | sim | prefixo atual `msg-` | Mensagem persistida, usada para historico e feedback. |

Exemplo com resposta fundamentada:

```json
{
  "answer": "Para abrir um chamado, acesse o portal de suporte interno, escolha a categoria do problema, descreva o impacto e anexe evidencias quando existirem.",
  "fallback": false,
  "intent": "procedimento",
  "confidence": 0.87,
  "sources": [
    {
      "document_id": "doc-001",
      "title": "Procedimento de abertura de chamado",
      "version": "1.0",
      "score": 0.91
    }
  ],
  "attendance_id": "att-123",
  "message_id": "msg-456"
}
```

Exemplo com fallback:

```json
{
  "answer": "Nao encontrei base suficiente para responder com seguranca. Posso encaminhar este atendimento para um humano.",
  "fallback": true,
  "intent": "procedimento",
  "confidence": 0.0,
  "sources": [],
  "attendance_id": "att-123",
  "message_id": "msg-456"
}
```

## SourceResponse

Cada item de `sources` representa um documento recuperado pelo RAG e usado
como evidencia da resposta.

| Campo | Tipo | Obrigatorio | Regra | Descricao |
|---|---|---:|---|---|
| `document_id` | string | sim | identificador do documento | Documento de conhecimento usado. |
| `title` | string | sim | texto | Titulo do documento usado na resposta. |
| `version` | string | sim | texto | Versao do documento no momento da resposta. |
| `score` | number | sim | 0.0 a 1.0 | Relevancia do trecho/documento recuperado. |

## Enums oficiais

### Channel

| Valor | Uso |
|---|---|
| `web` | Perguntas enviadas pela interface React. |
| `telegram` | Perguntas recebidas pelo bot Telegram. |

### Intent

| Valor | Uso |
|---|---|
| `saudacao` | Saudacao simples. |
| `procedimento` | Duvida ou pedido de procedimento coberto pela base. |
| `solicitacao_humana` | Usuario pediu atendimento humano. |
| `consulta_chamado` | Consulta de status de chamado. |
| `fora_de_escopo` | Tema fora do dominio da POC. |
| `desconhecida` | Intencao nao classificada. |

## Contrato do Telegram

O webhook do Telegram recebe somente os dados necessarios do canal e adapta a
entrada para `AskRequest` com `channel = "telegram"`.

Endpoint: `POST /telegram/webhook`

Entrada:

```json
{
  "user_id": "telegram-123456",
  "message": "Como abrir chamado no suporte?"
}
```

Saida: exatamente o mesmo formato de `AskResponse`.

## Regras de compatibilidade

- Novos campos em `AskRequest` ou `AskResponse` devem ser opcionais ate todos
  os clientes serem atualizados.
- Campos existentes nao devem mudar de nome, tipo ou significado sem nova
  versao de contrato.
- O frontend deve usar `message_id` para registrar feedback.
- Historico e metricas devem se apoiar em `attendance_id`, `message_id`,
  `intent`, `fallback`, `confidence` e `sources`.
- `fallback = true` com `sources = []` e o comportamento padrao para pergunta
  sem contexto confiavel.

## Criterios de aceite da S1-01

- Contrato de entrada e saida definido para Web e Telegram.
- Enums oficiais documentados.
- Campos obrigatorios, tipos e limites documentados.
- Backend e frontend possuem tipos equivalentes.
- Testes de contrato validam a estrutura retornada pela API.
