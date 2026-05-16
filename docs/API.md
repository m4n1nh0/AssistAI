# API — AssistAI

> **Base URL:** `http://localhost:8000`
> **Formato:** JSON
> **Prefix:** Nenhum (configurável via `ASSISTAI_API_PREFIX`)

---

## Índice

1. [POST /ask](#1-post-ask)
2. [POST /feedback](#2-post-feedback)
3. [GET /attendances](#3-get-attendances)
4. [GET /attendances/{id}](#4-get-attendancesid)
5. [GET /documents](#5-get-documents)
6. [POST /documents](#6-post-documents)
7. [POST /documents/reindex](#7-post-documentsreindex)
8. [GET /metrics](#8-get-metrics)
9. [GET /health](#9-get-health)
10. [POST /telegram/webhook](#10-post-telegramwebhook)

---

## 1. POST /ask

Endpoint principal do assistente. Recebe uma pergunta e retorna a resposta gerada pelo pipeline RAG + LLM.

### Request

```json
{
  "user_id": "web-user-123",
  "channel": "web",
  "message": "Como abrir um chamado no suporte?"
}
```

### Response (200)

```json
{
  "answer": "Para abrir um chamado, acesse o portal de suporte interno, escolha a categoria do problema, descreva o impacto e anexe evidencias quando existirem. O atendimento retorna um numero de protocolo para acompanhamento.",
  "fallback": false,
  "intent": "procedimento",
  "confidence": 0.8912,
  "sources": [
    {
      "document_id": "doc-a1b2c3d4e5f6",
      "title": "Procedimento de abertura de chamado",
      "version": "1.0",
      "score": 0.8912
    }
  ],
  "attendance_id": "att-f1e2d3c4b5a6",
  "message_id": "msg-9a8b7c6d5e4f"
}
```

### Response com Fallback (200)

```json
{
  "answer": "Nao encontrei na base de conhecimento informacao suficiente para responder a sua pergunta com seguranca.\n\nPosso:\n1. Encaminhar seu atendimento para um atendente humano.\n2. Ajudar com outro assunto dentro do escopo de suporte interno.",
  "fallback": true,
  "intent": "procedimento",
  "confidence": 0.0,
  "sources": [],
  "attendance_id": "att-a1b2c3d4e5f6",
  "message_id": "msg-6f5e4d3c2b1a"
}
```

### Campos

| Campo | Tipo | Descrição |
|---|---|---|
| `user_id` | `string` (1-128) | Identificador do usuário no canal |
| `channel` | `string` | `"web"` ou `"telegram"` |
| `message` | `string` (1-2000) | Texto da pergunta |

### Intenções Detectadas

| Intenção | Descrição | Gatilho |
|---|---|---|
| `procedimento` | Pergunta sobre procedimentos | Qualquer pergunta não classificada |
| `saudacao` | Saudação | "oi", "ola", "bom dia", etc. |
| `solicitacao_humana` | Solicitação de atendente | "humano", "atendente", "pessoa" |
| `consulta_chamado` | Consulta de chamado | "CHM-12345" |

---

## 2. POST /feedback

Registra feedback do usuário sobre uma resposta.

### Request

```json
{
  "message_id": "msg-9a8b7c6d5e4f",
  "useful": true,
  "comment": "Resolveu minha duvida rapidamente."
}
```

### Response (200)

```json
{
  "feedback_id": "fbk-1a2b3c4d5e6f",
  "message_id": "msg-9a8b7c6d5e4f",
  "useful": true,
  "created_at": "2026-05-16T14:30:00Z"
}
```

### Campos

| Campo | Tipo | Descrição |
|---|---|---|
| `message_id` | `string` | ID da mensagem avaliada |
| `useful` | `boolean` | `true` = útil, `false` = não útil |
| `comment` | `string` (opcional, max 1000) | Comentário do usuário |

---

## 3. GET /attendances

Lista todas as sessões de atendimento.

### Response (200)

```json
[
  {
    "attendance_id": "att-f1e2d3c4b5a6",
    "user_id": "usr-1a2b3c4d5e6f",
    "channel": "web",
    "escalated": false,
    "started_at": "2026-05-16T14:28:00Z",
    "message_count": 3
  }
]
```

---

## 4. GET /attendances/{id}

Retorna detalhes de um atendimento com todas as mensagens.

### Response (200)

```json
{
  "attendance_id": "att-f1e2d3c4b5a6",
  "user_id": "usr-1a2b3c4d5e6f",
  "channel": "web",
  "escalated": false,
  "started_at": "2026-05-16T14:28:00Z",
  "messages": [
    {
      "message_id": "msg-9a8b7c6d5e4f",
      "user_message": "Como abrir chamado?",
      "assistant_answer": "Para abrir um chamado...",
      "fallback": false,
      "intent": "procedimento",
      "confidence": 0.89,
      "sources": [],
      "created_at": "2026-05-16T14:28:01Z"
    }
  ]
}
```

---

## 5. GET /documents

Lista todos os documentos da base de conhecimento.

### Response (200)

```json
[
  {
    "document_id": "doc-a1b2c3d4e5f6",
    "title": "Procedimento de abertura de chamado",
    "category": "help-desk",
    "channel": "both",
    "version": "1.0",
    "status": "active",
    "updated_at": "2026-05-16T14:00:00Z",
    "source": "manual",
    "owner": "suporte",
    "sensitivity": "interno",
    "tags": ["chamado", "portal", "suporte"]
  }
]
```

---

## 6. POST /documents

Cria um novo documento na base de conhecimento.

### Request

```json
{
  "title": "Procedimento de devolucao",
  "category": "help-desk",
  "channel": "both",
  "version": "1.0",
  "status": "active",
  "source": "manual",
  "owner": "suporte",
  "sensitivity": "interno",
  "content": "Para solicitar devolucao, acesse o portal...",
  "tags": ["devolucao", "troca"]
}
```

### Response (201)

```json
{
  "document_id": "doc-9a8b7c6d5e4f",
  "title": "Procedimento de devolucao",
  "category": "help-desk",
  "channel": "both",
  "version": "1.0",
  "status": "active",
  "updated_at": "2026-05-16T14:35:00Z",
  "source": "manual",
  "owner": "suporte",
  "sensitivity": "interno",
  "tags": ["devolucao", "troca"]
}
```

---

## 7. POST /documents/reindex

Reindexa todos os documentos no Qdrant (re-chunk + re-embed).

### Response (200)

```json
{
  "indexed_documents": 5,
  "indexed_chunks": 8
}
```

---

## 8. GET /metrics

Retorna métricas operacionais do assistente.

### Response (200)

```json
{
  "total_attendances": 42,
  "total_messages": 156,
  "fallback_rate": 0.12,
  "useful_feedback_rate": 0.78,
  "escalated_attendances": 5,
  "top_intents": {
    "procedimento": 120,
    "saudacao": 20,
    "consulta_chamado": 10,
    "solicitacao_humana": 6
  },
  "top_documents": {
    "Procedimento de abertura de chamado": 45,
    "Reset de senha": 32
  },
  "unanswered_questions": [
    "Qual e a capital da Franca?"
  ]
}
```

---

## 9. GET /health

Health check simples.

### Response (200)

```json
{
  "status": "ok"
}
```

---

## 10. POST /telegram/webhook

Webhook para mensagens do Telegram. Reutiliza o mesmo motor do endpoint `/ask`.

### Request

```json
{
  "user_id": "tg-user-456",
  "message": "Como resetar minha senha?"
}
```

### Response (200)

Mesma estrutura de `POST /ask`.

```json
{
  "answer": "Para solicitar reset de senha, use a opcao de recuperacao...",
  "fallback": false,
  "intent": "procedimento",
  "confidence": 0.75,
  "sources": [...],
  "attendance_id": "att-...",
  "message_id": "msg-..."
}
```

---

## Erros

### 422 — Validation Error

```json
{
  "detail": [
    {
      "loc": ["body", "message"],
      "msg": "String should have at most 2000 characters",
      "type": "string_too_long"
    }
  ]
}
```

### 500 — Internal Server Error

Retornado apenas em casos excepcionais. O sistema tenta sempre retornar uma resposta amigável mesmo em caso de falha do LLM.
