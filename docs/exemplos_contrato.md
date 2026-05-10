# Exemplos de Uso do Contrato Oficial

## Visão Geral

Este documento fornece exemplos práticos de como usar o contrato de Pergunta e Resposta em Python (backend), TypeScript (frontend) e JSON bruto.

## Python (Backend - Pydantic)

### Criar uma Requisição

```python
from datetime import datetime
from app.domain.contracts import AskRequest, RequestMetadata
from app.domain.enums import Channel

# Forma 1: Construindo com o modelo Pydantic
metadata = RequestMetadata(
    timestamp=datetime.utcnow(),
    user_agent="Mozilla/5.0...",
    ip_address="192.168.1.1"
)

request = AskRequest(
    version="1.0",
    question="Como reiniciar o servidor?",
    user_id="user123",
    channel=Channel.WEB,
    conversation_id="conv456",
    metadata=metadata
)

# Forma 2: A partir de JSON (Pydantic valida automaticamente)
import json

request_json = {
    "version": "1.0",
    "question": "Como reiniciar o servidor?",
    "user_id": "user123",
    "channel": "web",
    "conversation_id": "conv456",
    "metadata": {
        "timestamp": "2024-01-01T12:00:00Z",
        "user_agent": "Mozilla/5.0..."
    }
}

request = AskRequest(**request_json)
```

### Criar uma Resposta

```python
from datetime import datetime
from app.domain.contracts import (
    AskResponse,
    SourceResponse,
    ResponseMetadata,
)

sources = [
    SourceResponse(
        document_id="doc001",
        title="Guia de Manutenção",
        content="Para reiniciar: systemctl restart app-server",
        score=0.95,
        version="1.2"
    )
]

metadata = ResponseMetadata(
    processing_time_ms=250,
    model_used="gpt-4",
    timestamp=datetime.utcnow()
)

response = AskResponse(
    version="1.0",
    answer="Para reiniciar o servidor de aplicação, execute: systemctl restart app-server",
    sources=sources,
    score=0.9,
    fallback=False,
    conversation_id="conv456",
    metadata=metadata
)

# Serializar para JSON
response_json = response.model_dump(mode="json")
print(json.dumps(response_json, default=str))
```

### Resposta com Fallback

```python
from datetime import datetime
from app.domain.contracts import AskResponse, ResponseMetadata
from app.domain.contracts import FallbackReason

metadata = ResponseMetadata(
    processing_time_ms=150,
    model_used="fallback",
    timestamp=datetime.utcnow()
)

fallback_response = AskResponse(
    version="1.0",
    answer="Desculpe, não encontrei informações suficientes.",
    sources=[],
    score=0.1,
    fallback=True,
    fallback_reason=FallbackReason.LOW_SCORE,
    metadata=metadata
)
```

### Manipular Erros

```python
from app.domain.contracts import ErrorResponse, ErrorCode

error_response = {
    "version": "1.0",
    "error": {
        "code": ErrorCode.QUESTION_TOO_LONG,
        "message": "A pergunta excede 1000 caracteres",
        "details": {
            "field": "question",
            "max_length": 1000
        }
    }
}

response = ErrorResponse(**error_response)
```

### Validação Automática

```python
from pydantic import ValidationError

# Isso vai gerar erro de validação automáticamente
try:
    invalid_request = AskRequest(
        version="1.0",
        question="",  # Vazio - não permitido!
        channel="web",
        metadata={
            "timestamp": "2024-01-01T12:00:00Z"
        }
    )
except ValidationError as e:
    print(f"Erro de validação: {e}")
```

## TypeScript (Frontend)

### Criar uma Requisição

```typescript
import { AskRequest, createAskRequest, Channel } from "@/domain/contracts";

// Forma 1: Usando o factory
const request = createAskRequest(
  "Como reiniciar o servidor?",
  "web",
  "user123",
  "conv456"
);

// Forma 2: Construindo manualmente
const request: AskRequest = {
  version: "1.0",
  question: "Como reiniciar o servidor?",
  user_id: "user123",
  channel: "web",
  conversation_id: "conv456",
  metadata: {
    timestamp: new Date().toISOString(),
    user_agent: navigator.userAgent,
  },
};
```

### Enviar para API

```typescript
import { isAskResponse, isErrorResponse, AskResponse, ErrorResponse } from "@/domain/contracts";

async function askAssistant(request: AskRequest): Promise<AskResponse | ErrorResponse> {
  const response = await fetch("/api/ask", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(request),
  });

  const data = await response.json();

  if (isAskResponse(data)) {
    return data as AskResponse;
  } else if (isErrorResponse(data)) {
    return data as ErrorResponse;
  } else {
    throw new Error("Resposta inválida da API");
  }
}

// Usar
try {
  const response = await askAssistant(request);
  
  if (isAskResponse(response)) {
    console.log("Resposta:", response.answer);
    console.log("Fontes:", response.sources);
    console.log("Fallback:", response.fallback);
  } else if (isErrorResponse(response)) {
    console.error("Erro:", response.error.message);
  }
} catch (error) {
  console.error("Erro ao chamar API:", error);
}
```

### Processar Resposta com Feedback

```typescript
import { FeedbackRequest, createAskRequest } from "@/domain/contracts";

async function sendFeedback(
  messageId: string,
  useful: boolean,
  comment?: string
): Promise<void> {
  const feedback: FeedbackRequest = {
    message_id: messageId,
    useful,
    comment,
  };

  const response = await fetch("/api/feedback", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(feedback),
  });

  if (!response.ok) {
    throw new Error("Erro ao enviar feedback");
  }
}
```

## JSON Bruto (API Direta/Telegram)

### Exemplo de Requisição Web

```json
{
  "version": "1.0",
  "question": "Como reiniciar o servidor de aplicação?",
  "user_id": "user123",
  "channel": "web",
  "conversation_id": "conv456",
  "session_id": "sess789",
  "metadata": {
    "timestamp": "2024-01-01T12:00:00Z",
    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "ip_address": "192.168.1.100"
  }
}
```

### Exemplo de Requisição Telegram

```json
{
  "version": "1.0",
  "question": "Como reiniciar o servidor?",
  "user_id": "123456789",
  "channel": "telegram",
  "metadata": {
    "timestamp": "2024-01-01T12:00:00Z",
    "message_id": "987654321"
  }
}
```

### Exemplo de Resposta de Sucesso

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
    "timestamp": "2024-01-01T12:00:00.500Z"
  }
}
```

### Exemplo de Resposta com Fallback

```json
{
  "version": "1.0",
  "answer": "Desculpe, não encontrei informações suficientes na base de conhecimento para responder sua pergunta com segurança. Recomendo consultar o suporte humano.",
  "sources": [],
  "score": 0.15,
  "fallback": true,
  "fallback_reason": "no_sources",
  "conversation_id": "conv456",
  "metadata": {
    "processing_time_ms": 180,
    "model_used": "fallback",
    "timestamp": "2024-01-01T12:00:00.500Z"
  }
}
```

### Exemplo de Erro

```json
{
  "version": "1.0",
  "error": {
    "code": "QUESTION_TOO_LONG",
    "message": "A pergunta excede o limite máximo de 1000 caracteres",
    "details": {
      "field": "question",
      "current_length": 1500,
      "max_length": 1000
    }
  }
}
```

## Integração com FastAPI (Backend)

### Endpoint da API

```python
from fastapi import APIRouter, HTTPException, status
from app.domain.contracts import AskRequest, AskResponse, ErrorResponse
from app.application.services import AskService

router = APIRouter(prefix="/api", tags=["assistant"])

@router.post("/ask", response_model=AskResponse)
async def ask(request: AskRequest) -> AskResponse:
    """
    Endpoint oficial de pergunta e resposta.
    
    - Valida automaticamente contra o contrato
    - Retorna resposta padronizada
    - Trata erros conforme o contrato
    """
    try:
        # Pydantic valida automaticamente o request
        service = AskService()
        response = await service.process_ask(request)
        return response
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "version": "1.0",
                "error": {
                    "code": "INVALID_REQUEST",
                    "message": str(e)
                }
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "version": "1.0",
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "Erro interno do servidor"
                }
            }
        )
```

## Testes Unitários

### Python (Pytest)

```python
import pytest
from datetime import datetime
from app.domain.contracts import AskRequest, AskResponse, RequestMetadata
from app.domain.enums import Channel

def test_ask_request_validation():
    """Testa validação do contrato de entrada."""
    # Válido
    request = AskRequest(
        version="1.0",
        question="Teste",
        channel=Channel.WEB,
        metadata=RequestMetadata(timestamp=datetime.utcnow())
    )
    assert request.question == "Teste"

def test_ask_request_question_too_long():
    """Testa limite de caracteres."""
    with pytest.raises(ValueError):
        AskRequest(
            version="1.0",
            question="x" * 1001,  # Excede 1000
            channel=Channel.WEB,
            metadata=RequestMetadata(timestamp=datetime.utcnow())
        )

def test_ask_request_empty_question():
    """Testa rejeição de pergunta vazia."""
    with pytest.raises(ValueError):
        AskRequest(
            version="1.0",
            question="   ",  # Apenas espaços
            channel=Channel.WEB,
            metadata=RequestMetadata(timestamp=datetime.utcnow())
        )
```

### TypeScript (Jest)

```typescript
import { createAskRequest, isAskResponse, isErrorResponse } from "@/domain/contracts";

describe("AskRequest", () => {
  test("createAskRequest deve gerar request válido", () => {
    const request = createAskRequest("Teste", "web", "user123");
    expect(request.version).toBe("1.0");
    expect(request.question).toBe("Teste");
    expect(request.channel).toBe("web");
    expect(request.metadata.timestamp).toBeDefined();
  });

  test("createAskRequest deve trimmar a pergunta", () => {
    const request = createAskRequest("  Teste  ", "web");
    expect(request.question).toBe("Teste");
  });
});

describe("Type Guards", () => {
  test("isAskResponse deve identificar resposta válida", () => {
    const response = {
      version: "1.0",
      answer: "Teste",
      sources: [],
      score: 0.5,
      fallback: false,
      metadata: {
        processing_time_ms: 100,
        model_used: "test",
        timestamp: new Date().toISOString(),
      },
    };
    expect(isAskResponse(response)).toBe(true);
  });

  test("isErrorResponse deve identificar erro válido", () => {
    const error = {
      version: "1.0",
      error: {
        code: "INVALID_REQUEST",
        message: "Teste",
      },
    };
    expect(isErrorResponse(error)).toBe(true);
  });
});
```

## Checklist de Implementação

- [ ] Backend implementado com Pydantic models
- [ ] Frontend implementado com interfaces TypeScript
- [ ] Validação automática funcionando
- [ ] Testes de contrato passando
- [ ] Documentação de integração atualizada
- [ ] Equipes (Web, Telegram, IA) revisaram e aprovaram
- [ ] Rate limiting implementado
- [ ] Auditoria/logging implementado
- [ ] Exemplos funcionando end-to-end
