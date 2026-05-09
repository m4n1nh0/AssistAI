# Contrato Oficial de Pergunta e Resposta do Assistente Inteligente

## Visão Geral

Este documento define o contrato padrão para a comunicação entre os componentes do Assistente de Atendimento Inteligente: Web, Telegram, API e Motor de IA. O objetivo é padronizar a entrada e saída de dados em formato JSON, garantindo consistência, evitando retrabalho e facilitando a integração entre equipes.

Todos os endpoints e interfaces devem seguir este contrato para garantir interoperabilidade.

**Versão do Contrato**: 1.0 (Data: 2024-01-01)

## Formato Geral

- **Protocolo**: HTTP/HTTPS para API
- **Método**: POST
- **Content-Type**: application/json
- **Encoding**: UTF-8

## Entrada (Request)

### Estrutura JSON

```json
{
  "version": "1.0",
  "question": "string (obrigatório)",
  "user_id": "string (opcional)",
  "channel": "string (obrigatório)",
  "session_id": "string (opcional)",
  "conversation_id": "string (opcional)",
  "metadata": {
    "timestamp": "string (obrigatório, formato ISO 8601)",
    "user_agent": "string (opcional)",
    "ip_address": "string (opcional)",
    "message_id": "string (opcional, para Telegram)"
  }
}
```

### Campos

| Campo | Tipo | Obrigatório | Descrição | Validação |
|-------|------|-------------|-----------|-----------|
| `version` | string | Sim | Versão do contrato | Deve ser "1.0" |
| `question` | string | Sim | A pergunta do usuário | Máximo 1000 caracteres, não vazio após trim |
| `user_id` | string | Não | Identificador único do usuário | Máximo 255 caracteres |
| `channel` | string | Sim | Canal de origem | Valores permitidos: "web", "telegram" |
| `session_id` | string | Não | ID da sessão de conversa | Máximo 255 caracteres |
| `conversation_id` | string | Não | ID da conversa para multi-turno | Máximo 255 caracteres |
| `metadata` | object | Sim | Metadados adicionais | Objeto obrigatório com timestamp |
| `metadata.timestamp` | string | Sim | Timestamp da requisição | Formato ISO 8601 |
| `metadata.user_agent` | string | Não | User agent do cliente | |
| `metadata.ip_address` | string | Não | Endereço IP do cliente | |
| `metadata.message_id` | string | Não | ID da mensagem (Telegram) | |

### Regras de Validação da Entrada

- `question` deve ter entre 1 e 1000 caracteres após trim
- `channel` deve ser exatamente "web" ou "telegram"
- `metadata.timestamp` deve ser uma data válida em ISO 8601
- Todos os campos string devem ser trimmed
- Não aceitar caracteres de controle ou scripts maliciosos (sanitização básica)
- Rate limiting: Máximo 10 requisições por minuto por user_id

## Saída (Response)

### Estrutura JSON de Sucesso

```json
{
  "version": "1.0",
  "answer": "string",
  "sources": [
    {
      "document_id": "string",
      "title": "string",
      "content": "string",
      "score": "number",
      "version": "string"
    }
  ],
  "score": "number",
  "fallback": "boolean",
  "fallback_reason": "string (opcional)",
  "conversation_id": "string (opcional)",
  "metadata": {
    "processing_time_ms": "number",
    "model_used": "string",
    "timestamp": "string"
  }
}
```

### Estrutura JSON de Erro

```json
{
  "version": "1.0",
  "error": {
    "code": "string",
    "message": "string",
    "details": "object (opcional)"
  }
}
```

### Campos de Sucesso

| Campo | Tipo | Obrigatório | Descrição |
|-------|------|-------------|-----------|
| `version` | string | Sim | Versão do contrato |
| `answer` | string | Sim | Resposta gerada pelo assistente |
| `sources` | array | Sim | Lista de fontes utilizadas (pode ser vazia) |
| `sources[].document_id` | string | Sim | ID do documento fonte |
| `sources[].title` | string | Sim | Título do documento |
| `sources[].content` | string | Sim | Trecho relevante do documento |
| `sources[].score` | number | Sim | Score de relevância (0.0 a 1.0) |
| `sources[].version` | string | Sim | Versão do documento |
| `score` | number | Sim | Score geral da resposta (0.0 a 1.0) |
| `fallback` | boolean | Sim | Indica se foi usado fallback |
| `fallback_reason` | string | Não | Razão do fallback (ex: "low_score", "no_sources") |
| `conversation_id` | string | Não | ID da conversa para continuidade |
| `metadata` | object | Sim | Metadados da resposta |

### Campos de Erro

| Campo | Tipo | Obrigatório | Descrição |
|-------|------|-------------|-----------|
| `version` | string | Sim | Versão do contrato |
| `error.code` | string | Sim | Código do erro |
| `error.message` | string | Sim | Mensagem descritiva do erro |
| `error.details` | object | Não | Detalhes adicionais do erro |

### Regras de Validação da Saída

- `answer` deve ter no máximo 4000 caracteres
- `score` deve estar entre 0.0 e 1.0
- `sources` pode ser array vazio se não houver fontes confiáveis
- `fallback` deve ser true se score < 0.3 ou não houver sources válidas
- `metadata.processing_time_ms` deve ser um número positivo
- Limite de sources: Máximo 5 itens para evitar payloads grandes

## Mensagens de Erro

### Códigos de Erro Padrão

| Código | HTTP Status | Descrição |
|--------|-------------|-----------|
| `INVALID_REQUEST` | 400 | Requisição malformada ou inválida |
| `QUESTION_TOO_LONG` | 400 | Pergunta excede limite de caracteres |
| `UNSUPPORTED_CHANNEL` | 400 | Canal não suportado |
| `SERVICE_UNAVAILABLE` | 503 | Serviço temporariamente indisponível |
| `INTERNAL_ERROR` | 500 | Erro interno do servidor |
| `RATE_LIMIT_EXCEEDED` | 429 | Limite de requisições excedido |

### Exemplos de Erro

```json
{
  "version": "1.0",
  "error": {
    "code": "INVALID_REQUEST",
    "message": "Campo 'question' é obrigatório",
    "details": {
      "field": "question"
    }
  }
}
```

## Fallback

O fallback é ativado quando:

- Score geral < 0.3 (limite configurável)
- Não há fontes com score > 0.5
- Erro na geração da resposta

### Resposta de Fallback

```json
{
  "version": "1.0",
  "answer": "Desculpe, não encontrei informações suficientes na base de conhecimento para responder sua pergunta com segurança. Recomendo consultar o suporte humano.",
  "sources": [],
  "score": 0.0,
  "fallback": true,
  "fallback_reason": "low_score",
  "conversation_id": "conv123",
  "metadata": {
    "processing_time_ms": 150,
    "model_used": "fallback",
    "timestamp": "2024-01-01T12:00:00Z"
  }
}
```

## Regras Principais de Validação

1. **Sanitização**: Todas as entradas devem ser sanitizadas contra XSS e injeção
2. **Limites**: Respeitar limites de tamanho para prevenir ataques DoS
3. **Autenticação**: Canais externos (Telegram) devem validar tokens de webhook
4. **Rate Limiting**: Implementar controle de taxa por user_id (10 req/min)
5. **Auditoria**: Todas as interações devem ser logadas com timestamp
6. **Consistência**: Mesmo contrato para Web, Telegram e API direta
7. **Versionamento**: Sempre incluir version para compatibilidade

## Integração por Canal

### Web
- Frontend envia JSON diretamente conforme contrato
- `channel`: "web"
- `conversation_id`: Gerado pelo frontend para sessões

### Telegram
- Webhook recebe update do Telegram, mapear para request:
  - `question`: update.message.text
  - `user_id`: update.message.from.id
  - `channel`: "telegram"
  - `metadata.message_id`: update.message.message_id
- Resposta deve ser enviada de volta via Telegram API

## Schema JSON (Recomendado)

Para validação automática, use este schema simplificado:

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "version": {"type": "string", "enum": ["1.0"]},
    "question": {"type": "string", "minLength": 1, "maxLength": 1000},
    "channel": {"type": "string", "enum": ["web", "telegram"]},
    "metadata": {
      "type": "object",
      "properties": {
        "timestamp": {"type": "string", "format": "date-time"}
      },
      "required": ["timestamp"]
    }
  },
  "required": ["version", "question", "channel", "metadata"]
}
```

## Exemplos Completos

### Exemplo de Request (Web)

```json
{
  "version": "1.0",
  "question": "Como reiniciar o servidor de aplicação?",
  "user_id": "user123",
  "channel": "web",
  "conversation_id": "conv456",
  "metadata": {
    "timestamp": "2024-01-01T12:00:00Z",
    "user_agent": "Mozilla/5.0..."
  }
}
```

### Exemplo de Response de Sucesso

```json
{
  "version": "1.0",
  "answer": "Para reiniciar o servidor de aplicação, execute o comando 'systemctl restart app-server' no terminal.",
  "sources": [
    {
      "document_id": "doc001",
      "title": "Guia de Manutenção de Servidores",
      "content": "Para reiniciar serviços: systemctl restart [service-name]",
      "score": 0.95,
      "version": "1.2"
    }
  ],
  "score": 0.9,
  "fallback": false,
  "conversation_id": "conv456",
  "metadata": {
    "processing_time_ms": 250,
    "model_used": "gpt-4",
    "timestamp": "2024-01-01T12:00:00Z"
  }
}
```

### Exemplo de Response com Fallback

```json
{
  "version": "1.0",
  "answer": "Desculpe, não tenho informações suficientes sobre esse tópico específico.",
  "sources": [],
  "score": 0.1,
  "fallback": true,
  "fallback_reason": "no_sources",
  "conversation_id": "conv456",
  "metadata": {
    "processing_time_ms": 180,
    "model_used": "fallback",
    "timestamp": "2024-01-01T12:00:00Z"
  }
}
```

## Implementação

- **Backend**: Usar Pydantic models no FastAPI para validação automática
- **Web/Telegram**: Adaptar dados do usuário para o formato JSON
- **IA**: Receber entrada padronizada, retornar saída padronizada
- **Testes**: Incluir testes de contrato com JSON Schema

Este contrato deve ser versionado e evoluir conforme necessidades, mantendo compatibilidade backward.
  "sources": [
    {
      "document_id": "doc001",
      "title": "Guia de Manutenção de Servidores",
      "content": "Para reiniciar serviços: systemctl restart [service-name]",
      "score": 0.95,
      "version": "1.2"
    }
  ],
  "score": 0.9,
  "fallback": false,
  "metadata": {
    "processing_time_ms": 250,
    "model_used": "gpt-4",
    "timestamp": "2024-01-01T12:00:00Z"
  }
}
```

### Exemplo de Response com Fallback

```json
{
  "answer": "Desculpe, não tenho informações suficientes sobre esse tópico específico.",
  "sources": [],
  "score": 0.1,
  "fallback": true,
  "metadata": {
    "processing_time_ms": 180,
    "model_used": "fallback",
    "timestamp": "2024-01-01T12:00:00Z"
  }
}
```

## Implementação

- **Backend**: Validar entrada, processar, gerar saída conforme contrato
- **Web/Telegram**: Adaptar dados do usuário para o formato JSON
- **IA**: Receber entrada padronizada, retornar saída padronizada
- **Testes**: Incluir testes de contrato para validar conformidade

Este contrato deve ser versionado e evoluir conforme necessidades, mantendo compatibilidade backward.