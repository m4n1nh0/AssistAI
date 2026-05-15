# Contrato oficial de pergunta e resposta do assistente

## Objetivo

Padronizar a comunicacao entre Web, Telegram, API e motor de IA no fluxo principal de atendimento. Toda frente deve tratar `AskRequest` e `AskResponse` como a fonte oficial para troca de mensagens com o assistente.

## Versao

| Campo | Valor |
|---|---|
| `schema_version` | `assistant.ask.v1` |
| Backend | `backend/app/domain/contracts.py` |
| Frontend | `frontend/src/domain/contracts.ts` |
| Endpoint Web/API | `POST /ask` |
| Endpoint Telegram | `POST /telegram/webhook`, convertido internamente para `AskRequest` |

## AskRequest

```json
{
  "schema_version": "assistant.ask.v1",
  "request_id": "req-web-001",
  "user_id": "web-user-001",
  "channel": "web",
  "message": "Como abrir chamado no suporte?",
  "context": {
    "conversation_id": "chat-123",
    "external_message_id": "message-456",
    "locale": "pt-BR",
    "metadata": {
      "origin": "web-chat"
    }
  }
}
```

| Campo | Obrigatorio | Regra |
|---|---:|---|
| `schema_version` | Nao | Default `assistant.ask.v1`; rejeita versoes diferentes. |
| `request_id` | Nao | ID de correlacao gerado pelo canal consumidor. |
| `user_id` | Sim | Identificador do usuario no canal de origem, entre 1 e 128 caracteres. |
| `channel` | Nao | `web` ou `telegram`; default `web`. |
| `message` | Sim | Pergunta original do usuario, entre 1 e 2000 caracteres. |
| `context.conversation_id` | Nao | ID externo da conversa quando o canal possuir esse conceito. |
| `context.external_message_id` | Nao | ID externo da mensagem recebida no canal. |
| `context.locale` | Nao | Default `pt-BR`. |
| `context.metadata` | Nao | Pares chave/valor simples para dados nao sensiveis do canal. |

## AskResponse

```json
{
  "schema_version": "assistant.ask.v1",
  "request_id": "req-web-001",
  "user_id": "web-user-001",
  "channel": "web",
  "answer": "Para abrir um chamado, acesse o portal de suporte interno...",
  "fallback": false,
  "handoff_required": false,
  "intent": "procedimento",
  "confidence": 0.92,
  "sources": [
    {
      "document_id": "doc-123",
      "title": "Procedimento de abertura de chamado",
      "version": "1.0",
      "score": 0.92
    }
  ],
  "attendance_id": "att-123",
  "message_id": "msg-123",
  "generated_at": "2026-05-15T12:00:00Z"
}
```

| Campo | Regra |
|---|---|
| `schema_version` | Sempre `assistant.ask.v1`. |
| `request_id` | Ecoa o ID recebido, quando informado. |
| `user_id` | Ecoa o usuario recebido no canal. |
| `channel` | Canal efetivamente usado no processamento. |
| `answer` | Texto final para exibir ao usuario. |
| `fallback` | `true` quando nao houve base suficiente ou quando o fluxo exige fallback controlado. |
| `handoff_required` | `true` quando o atendimento foi marcado para escalonamento humano. |
| `intent` | Intencao classificada pelo motor. |
| `confidence` | Numero entre 0 e 1. |
| `sources` | Lista de documentos usados na resposta, com score entre 0 e 1. |
| `attendance_id` | ID interno do atendimento persistido. |
| `message_id` | ID interno da mensagem/resposta, usado tambem no feedback. |
| `generated_at` | Data/hora UTC de geracao da resposta. |

## Regras de uso

- Web deve chamar `POST /ask` usando `channel = web`.
- Telegram deve receber o webhook em seu formato minimo e converter para `AskRequest` com `channel = telegram`.
- O motor de IA deve depender de `AskRequest`, nunca de payloads especificos de canal.
- Novos campos devem ser opcionais em `assistant.ask.v1`; mudancas obrigatorias exigem nova `schema_version`.
- Dados sensiveis nao devem ser enviados em `context.metadata`.
- Feedback deve usar `message_id` retornado no `AskResponse`.
