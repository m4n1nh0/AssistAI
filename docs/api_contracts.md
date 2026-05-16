# Contratos iniciais da API

## POST /ask

Entrada:

```json
{
  "user_id": "web-user-001",
  "channel": "web",
  "message": "Como faço para abrir um chamado?"
}
```

Saída:

```json
{
  "answer": "Resposta do assistente",
  "fallback": false,
  "intent": "procedimento",
  "confidence": 0.75,
  "sources": [
    {
      "document_id": "abertura_chamado",
      "title": "Procedimento de abertura de chamado",
      "version": "1.0",
      "score": 0.5
    }
  ],
  "attendance_id": "att-...",
  "message_id": "msg-..."
}
```

## POST /feedback

```json
{
  "message_id": "msg-...",
  "useful": true,
  "comment": "Resposta resolveu minha dúvida."
}
```

## GET /attendances

Lista atendimentos em memória.

## GET /documents

Lista documentos carregados de `docs/knowledge_base` ou criados via API.

## POST /documents/reindex

Retorna contagem de documentos e chunks. A integração real com Qdrant entra na próxima fatia.

## POST /telegram/webhook

Webhook simplificado para validar reaproveitamento do fluxo do `/ask`.
