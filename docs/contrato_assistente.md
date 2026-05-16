# Contrato oficial do assistente

## Endpoint

```http
POST /ask
```

## Objetivo

Padronizar a comunicação entre Web, Telegram, API e motor de IA/RAG.

Este contrato define o formato oficial de envio de perguntas e recebimento de respostas do assistente. A partir desta definição, todos os canais devem seguir o mesmo padrão para evitar divergências entre frontend, integrações e backend.

---

## Request

```json
{
  "question": "Como faço para redefinir minha senha?",
  "channel": "web",
  "conversation_id": "conv_123456",
  "user": {
    "id": "user_001",
    "name": "Vinícius Almeida"
  },
  "metadata": {
    "telegram_chat_id": null,
    "page_url": "http://localhost:5173/chat"
  }
}
```

## Campos da Request

| Campo | Tipo | Obrigatório | Descrição |
|---|---|---:|---|
| `question` | string | Sim | Pergunta enviada pelo usuário. Substitui o campo antigo `message`. |
| `channel` | string | Sim | Canal de origem da pergunta. |
| `conversation_id` | string/null | Não | Identificador da conversa. Caso não seja enviado, a API pode gerar um valor padrão. |
| `user` | object/null | Não | Dados básicos do usuário. |
| `user.id` | string/null | Não | Identificador do usuário. Substitui o campo antigo `user_id` na raiz da request. |
| `user.name` | string/null | Não | Nome do usuário, quando disponível. |
| `metadata` | object | Não | Dados extras do canal ou da integração. |

---

## Response de sucesso

```json
{
  "answer": "Resposta final do assistente.",
  "status": "answered",
  "conversation_id": "conv_123456",
  "message_id": "msg_789",
  "sources": [],
  "usage": null,
  "metadata": {
    "channel": "web"
  }
}
```

## Campos da Response

| Campo | Tipo | Obrigatório | Descrição |
|---|---|---:|---|
| `answer` | string | Sim | Resposta final que será exibida ao usuário. |
| `status` | string | Sim | Estado da resposta. Substitui o campo antigo `fallback`. |
| `conversation_id` | string | Sim | Identificador da conversa. |
| `message_id` | string | Sim | Identificador da resposta/mensagem gerada. |
| `sources` | array | Sim | Fontes recuperadas pelo RAG. Na S1-01 pode retornar vazio. |
| `usage` | object/null | Não | Informações de uso do modelo, quando disponíveis. |
| `metadata` | object | Sim | Informações técnicas ou complementares da execução. |

---

## Status possíveis

- `answered`: resposta gerada normalmente.
- `fallback`: não houve contexto confiável suficiente para responder.
- `error`: erro técnico ou falha de processamento.

Exemplo:

```json
{
  "status": "answered"
}
```

> Mudança importante: o contrato novo usa `status` no lugar de `fallback: true/false`.

---

## Canais aceitos

- `web`
- `telegram`
- `api`

Exemplo válido:

```json
{
  "channel": "web"
}
```

Exemplo inválido:

```json
{
  "channel": "whatsapp"
}
```

---

## Mudanças documentadas no contrato

O contrato oficial atualizado define as seguintes mudanças:

| Antes | Agora |
|---|---|
| `message` | `question` |
| `user_id` na raiz da request | `user.id` dentro do objeto `user` |
| `fallback: true/false` | `status: "answered"`, `"fallback"` ou `"error"` |
| Resposta sem padrão único | Toda resposta retorna `answer`, `status`, `conversation_id`, `message_id`, `sources` e `metadata` |

---

## Exemplo do contrato antigo

Este formato não deve ser usado no contrato novo:

```json
{
  "user_id": "web-user-001",
  "channel": "web",
  "message": "Como abrir chamado no suporte?"
}
```

Também não deve ser esperado este formato de resposta:

```json
{
  "fallback": false
}
```

---

## Exemplo do contrato novo

Formato oficial da request:

```json
{
  "question": "Como abrir chamado no suporte?",
  "channel": "web",
  "conversation_id": "conv_test_001",
  "user": {
    "id": "web-user-001"
  },
  "metadata": {}
}
```

Formato oficial da response:

```json
{
  "answer": "Resposta final do assistente.",
  "status": "answered",
  "conversation_id": "conv_test_001",
  "message_id": "msg_789",
  "sources": [],
  "usage": null,
  "metadata": {
    "channel": "web"
  }
}
```

---

## Regras

- Toda pergunta deve passar pelo endpoint `/ask`.
- Web e Telegram não devem chamar diretamente o motor de IA.
- O campo oficial da pergunta é `question`.
- O campo `message` não deve ser usado no novo contrato.
- O identificador do usuário deve ficar em `user.id`.
- O campo `user_id` não deve ser enviado diretamente na raiz da request.
- Toda resposta deve retornar `status`.
- O campo `fallback` foi substituído por `status`.
- Toda resposta deve retornar `conversation_id`.
- Toda resposta deve retornar `message_id`.
- Toda resposta deve retornar `sources`, mesmo que seja uma lista vazia.
- Fontes recuperadas pelo RAG devem ser retornadas em `sources`.
- Toda resposta deve retornar `metadata`.

---

## Validações principais

### Pergunta válida

```json
{
  "question": "Como abrir chamado no suporte?",
  "channel": "web"
}
```

### Pergunta inválida

```json
{
  "question": "",
  "channel": "web"
}
```

Resultado esperado:

```http
422 Unprocessable Entity
```

### Canal inválido

```json
{
  "question": "Como abrir chamado?",
  "channel": "whatsapp"
}
```

Resultado esperado:

```http
422 Unprocessable Entity
```

---

## Observação sobre fontes

Na task S1-01, o campo `sources` pode retornar vazio:

```json
{
  "sources": []
}
```

Quando o RAG for integrado, o formato esperado será:

```json
{
  "sources": [
    {
      "document_id": "doc_001",
      "title": "Manual de Suporte",
      "chunk_id": "chunk_001",
      "score": 0.87
    }
  ]
}
```

---

## Observação sobre feedback

O `message_id` retornado pelo `/ask` será usado futuramente para vincular feedback à resposta gerada.

Na S1-01, o endpoint pode retornar um `message_id` mockado apenas para validar o contrato. A persistência real do histórico e do feedback será tratada nas próximas tarefas.

---

## Critério de pronto da S1-01

A task é considerada pronta quando:

- O endpoint `POST /ask` existe.
- O contrato usa `question` em vez de `message`.
- O contrato usa `user.id` em vez de `user_id`.
- A resposta usa `status` em vez de `fallback`.
- A response retorna `answer`.
- A response retorna `conversation_id`.
- A response retorna `message_id`.
- A response retorna `sources`.
- A response retorna `metadata`.
- Os testes de contrato passam.
- O Ruff não aponta erros.