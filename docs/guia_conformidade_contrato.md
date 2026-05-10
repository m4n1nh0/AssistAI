# Guia de Conformidade com o Contrato Oficial

## Para todas as equipes: Web, Telegram, Backend e QA

### Visão Geral

Este documento é um guia prático para garantir que sua implementação está conforme o **Contrato Oficial de Pergunta e Resposta** versão 1.0.

**Arquivos de referência:**
- Contrato base: [`docs/contrato_pergunta_resposta.md`](contrato_pergunta_resposta.md)
- Exemplos de uso: [`docs/exemplos_contrato.md`](exemplos_contrato.md)
- Modelos Pydantic: [`backend/app/domain/contracts.py`](../backend/app/domain/contracts.py)
- Tipos TypeScript: [`frontend/src/domain/contracts.ts`](../frontend/src/domain/contracts.ts)
- Validadores: [`backend/app/infrastructure/validation.py`](../backend/app/infrastructure/validation.py)
- Testes: [`backend/tests/test_contract.py`](../backend/tests/test_contract.py)

---

## Para a Equipe de Backend (FastAPI)

### 1. Importar os Modelos

```python
from app.domain.contracts import (
    AskRequest,
    AskResponse,
    RequestMetadata,
    SourceResponse,
    ResponseMetadata,
    FeedbackRequest,
)
from app.infrastructure.validation import (
    validate_ask_request,
    validate_ask_response,
    build_success_response,
    build_fallback_response,
    sanitize_question,
)
```

### 2. Criar o Endpoint `/ask`

```python
from fastapi import APIRouter, HTTPException, status
from datetime import datetime
import time

router = APIRouter(prefix="/api", tags=["assistant"])

@router.post("/ask", response_model=AskResponse)
async def ask(request: AskRequest) -> AskResponse:
    """Endpoint oficial de pergunta e resposta."""
    
    start_time = time.time()
    
    try:
        # 1. Pydantic valida automaticamente
        validate_ask_request(request)
        
        # 2. Sanitizar pergunta
        clean_question = sanitize_question(request.question)
        
        # 3. Processar (busca RAG, LLM, etc.)
        sources = await rag_service.search(clean_question)
        
        # 4. Gerar resposta
        answer = await llm_service.generate(clean_question, sources)
        
        # 5. Calcular score
        score = calculate_score(sources)
        
        # 6. Construir resposta conforme contrato
        processing_time = int((time.time() - start_time) * 1000)
        
        response = build_success_response(
            question=clean_question,
            answer=answer,
            sources=sources,
            score=score,
            conversation_id=request.conversation_id,
            processing_time_ms=processing_time,
            model_used="gpt-4",
        )
        
        # 7. Validar resposta
        validate_ask_response(response)
        
        # 8. Log para auditoria
        await log_audit(request, response)
        
        return response
        
    except ValueError as e:
        # Erro de validação
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "version": "1.0",
                "error": {
                    "code": "INVALID_REQUEST",
                    "message": str(e),
                }
            },
        )
    except Exception as e:
        # Erro interno - retornar fallback
        processing_time = int((time.time() - start_time) * 1000)
        response = build_fallback_response(
            reason="error",
            processing_time_ms=processing_time,
        )
        await log_audit(request, response, error=str(e))
        return response
```

### 3. Implementar Feedback

```python
@router.post("/feedback", response_model=FeedbackResponse)
async def feedback(request: FeedbackRequest) -> FeedbackResponse:
    """Registrar feedback sobre uma resposta."""
    
    # Salvar feedback com link à resposta
    feedback_id = await feedback_service.save(
        message_id=request.message_id,
        useful=request.useful,
        comment=request.comment,
    )
    
    return FeedbackResponse(
        feedback_id=feedback_id,
        message_id=request.message_id,
        useful=request.useful,
        created_at=datetime.utcnow(),
    )
```

### 4. Checklist de Implementação Backend

- [ ] Modelos Pydantic importados
- [ ] Endpoint `/ask` retorna `AskResponse`
- [ ] Validação automática de entrada com Pydantic
- [ ] `validate_ask_response` chamado antes de retornar
- [ ] Fallback implementado com `build_fallback_response`
- [ ] `conversation_id` preservado e retornado
- [ ] `metadata.processing_time_ms` calculado
- [ ] Auditoria registra request e response
- [ ] Rate limiting implementado (10 req/min por user_id)
- [ ] Testes de contrato passando (`pytest backend/tests/test_contract.py`)

---

## Para a Equipe de Frontend (React + TypeScript)

### 1. Importar Tipos

```typescript
import {
  AskRequest,
  AskResponse,
  ErrorResponse,
  Channel,
  createAskRequest,
  isAskResponse,
  isErrorResponse,
} from "@/domain/contracts";
```

### 2. Hook de Chat

```typescript
import { useState } from "react";
import { createAskRequest, isAskResponse, isErrorResponse } from "@/domain/contracts";

export function useChat() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const sendMessage = async (question: string) => {
    setLoading(true);
    setError(null);

    try {
      // Criar request conforme contrato
      const request = createAskRequest(
        question,
        "web",
        localStorage.getItem("userId") || undefined
      );

      // Enviar para API
      const response = await fetch("/api/ask", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(request),
      });

      const data = await response.json();

      // Validar resposta com type guard
      if (isAskResponse(data)) {
        setMessages((prev) => [
          ...prev,
          {
            role: "assistant",
            content: data.answer,
            sources: data.sources,
            fallback: data.fallback,
            messageId: data.metadata.timestamp, // usar timestamp como ID
            timestamp: data.metadata.timestamp,
          },
        ]);
      } else if (isErrorResponse(data)) {
        setError(data.error.message);
      } else {
        setError("Resposta inválida da API");
      }
    } catch (err) {
      setError("Erro ao enviar mensagem");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return { messages, loading, error, sendMessage };
}
```

### 3. Componente de Chat

```typescript
import { useChat } from "@/application/hooks/useChat";
import { AskRequest } from "@/domain/contracts";

export function ChatPage() {
  const { messages, loading, sendMessage } = useChat();
  const [input, setInput] = useState("");

  const handleSend = async () => {
    if (!input.trim()) return;

    const question = input;
    setInput("");
    
    // Adicionar mensagem do usuário
    // ...
    
    // Enviar pergunta (função valida automaticamente)
    await sendMessage(question);
  };

  return (
    <div className="chat-container">
      {messages.map((msg) => (
        <div key={msg.id} className={`message ${msg.role}`}>
          {msg.content}
          {msg.sources && msg.sources.length > 0 && (
            <div className="sources">
              {msg.sources.map((src) => (
                <div key={src.document_id} className="source">
                  {src.title} (score: {(src.score * 100).toFixed(0)}%)
                </div>
              ))}
            </div>
          )}
          {msg.fallback && (
            <div className="warning">Resposta com fallback</div>
          )}
        </div>
      ))}
      <input
        type="text"
        value={input}
        onChange={(e) => setInput(e.target.value)}
        onKeyPress={(e) => e.key === "Enter" && handleSend()}
        disabled={loading}
        placeholder="Digite sua pergunta..."
      />
      <button onClick={handleSend} disabled={loading}>
        {loading ? "Enviando..." : "Enviar"}
      </button>
    </div>
  );
}
```

### 4. Checklist de Implementação Frontend

- [ ] Tipos TypeScript importados de `domain/contracts`
- [ ] `createAskRequest` usado para criar requisições
- [ ] Type guards (`isAskResponse`, `isErrorResponse`) usados
- [ ] `conversation_id` preservado entre mensagens
- [ ] Fontes (`sources`) exibidas quando disponíveis
- [ ] `fallback` indicado na UI
- [ ] Erros tratados adequadamente
- [ ] `metadata.timestamp` de cada resposta registrado

---

## Para a Equipe de Integrações (Telegram)

### 1. Webhook Receiver

```python
from fastapi import APIRouter, Request
from app.domain.contracts import AskRequest
from app.infrastructure.validation import map_telegram_to_ask_request

router = APIRouter(prefix="/api/telegram", tags=["telegram"])

@router.post("/webhook")
async def telegram_webhook(request: Request):
    """Receber updates do Telegram."""
    
    update = await request.json()
    
    if "message" not in update:
        return {"ok": True}
    
    try:
        # Mapear update do Telegram para AskRequest
        user_id = str(update["message"]["from"]["id"])
        ask_request = map_telegram_to_ask_request(
            update,
            user_id=user_id,
        )
        
        # Processar como qualquer outro request
        ask_service = AskService()
        response = await ask_service.process_ask(ask_request)
        
        # Enviar resposta de volta ao Telegram
        await send_telegram_message(
            chat_id=update["message"]["chat"]["id"],
            text=response.answer,
            sources=response.sources,
        )
        
        # Log para auditoria
        await log_audit(ask_request, response)
        
        return {"ok": True}
        
    except Exception as e:
        print(f"Erro ao processar Telegram: {e}")
        await send_telegram_message(
            chat_id=update["message"]["chat"]["id"],
            text="Desculpe, ocorreu um erro ao processar sua mensagem.",
        )
        return {"ok": False}
```

### 2. Enviar Resposta ao Telegram

```python
import aiohttp

async def send_telegram_message(
    chat_id: str,
    text: str,
    sources: list = None,
) -> None:
    """Enviar mensagem formatada ao Telegram."""
    
    # Formatar resposta
    message = text
    
    if sources and len(sources) > 0:
        message += "\n\n*Fontes:*\n"
        for src in sources[:3]:  # Limitar a 3 fontes
            message += f"• {src.title} (confiança: {int(src.score*100)}%)\n"
    
    # Enviar via Telegram API
    async with aiohttp.ClientSession() as session:
        await session.post(
            f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
            json={
                "chat_id": chat_id,
                "text": message,
                "parse_mode": "Markdown",
            },
        )
```

### 3. Checklist de Implementação Telegram

- [ ] `map_telegram_to_ask_request` usado para conversão
- [ ] `conversation_id` gerado para cada conversa do Telegram
- [ ] Response enviada de volta ao Telegram
- [ ] Erro de processamento tratado (enviar mensagem de fallback)
- [ ] Fontes exibidas em formato legível
- [ ] Auditoria registra canal="telegram"

---

## Para a Equipe de QA

### 1. Casos de Teste de Contrato

#### Entrada (Request)

```
✓ TC-001: Request válido com campos obrigatórios
  - version: "1.0"
  - question: "Como reiniciar?"
  - channel: "web"
  - metadata.timestamp válido
  
✓ TC-002: Request com campos opcionais
  - Incluir: user_id, conversation_id, metadata.user_agent
  
✗ TC-003: Request com question vazia
  - Deve retornar HTTP 400, erro INVALID_REQUEST
  
✗ TC-004: Request com question > 1000 caracteres
  - Deve retornar HTTP 400, erro QUESTION_TOO_LONG
  
✗ TC-005: Request com channel inválido
  - Deve retornar HTTP 400, erro UNSUPPORTED_CHANNEL
  
✗ TC-006: Request sem metadata.timestamp
  - Deve retornar HTTP 400, erro INVALID_REQUEST
```

#### Saída (Response)

```
✓ TC-101: Response sucesso com score > 0.3
  - fallback: false
  - sources: array com até 5 itens
  - score: entre 0.0 e 1.0
  
✓ TC-102: Response com fallback (score < 0.3)
  - fallback: true
  - fallback_reason: "low_score" ou "no_sources"
  - answer: mensagem padrão de fallback
  
✓ TC-103: Response registra tempo de processamento
  - metadata.processing_time_ms > 0
  
✓ TC-104: Response com conversas multi-turno
  - conversation_id preservado
```

#### Integração

```
✓ TC-201: Web envia request e recebe response
  - Fluxo Web → API → Response
  
✓ TC-202: Telegram envia mensagem e recebe resposta
  - Fluxo Telegram → Webhook → API → Telegram
  
✓ TC-203: Feedback vinculado à resposta
  - message_id referencia resposta anterior
```

### 2. Testes Automatizados

```bash
# Rodar testes de contrato
pytest backend/tests/test_contract.py -v

# Rodar com cobertura
pytest backend/tests/test_contract.py --cov=app.domain.contracts --cov=app.infrastructure.validation

# Validar específico
pytest backend/tests/test_contract.py::TestAskRequestContract -v
pytest backend/tests/test_contract.py::TestAskResponseContract -v
```

### 3. Checklist de QA

- [ ] Todos os testes de contrato passando
- [ ] Cobertura de testes > 80%
- [ ] Request/Response validam conforme schema JSON
- [ ] Integração Web funciona end-to-end
- [ ] Integração Telegram funciona end-to-end
- [ ] Erros retornam conforme contrato
- [ ] Fallback ativado corretamente
- [ ] Auditoria registra todas as interações

---

## Validação com curl (Local)

### Testar Endpoint `/ask`

```bash
# Request válido
curl -X POST http://localhost:8000/api/ask \
  -H "Content-Type: application/json" \
  -d '{
    "version": "1.0",
    "question": "Como reiniciar o servidor?",
    "user_id": "user123",
    "channel": "web",
    "metadata": {
      "timestamp": "2024-01-01T12:00:00Z"
    }
  }'

# Esperado: HTTP 200 com AskResponse conforme contrato

# Request inválido (question vazia)
curl -X POST http://localhost:8000/api/ask \
  -H "Content-Type: application/json" \
  -d '{
    "version": "1.0",
    "question": "",
    "channel": "web",
    "metadata": {
      "timestamp": "2024-01-01T12:00:00Z"
    }
  }'

# Esperado: HTTP 400 com ErrorResponse
```

### Testar Endpoint `/feedback`

```bash
curl -X POST http://localhost:8000/api/feedback \
  -H "Content-Type: application/json" \
  -d '{
    "message_id": "msg123",
    "useful": true,
    "comment": "Resposta correta"
  }'
```

---

## Perguntas Frequentes

**P: Como garanto que meu contrato está em conformidade?**  
R: Importe e use os modelos Pydantic (backend) ou interfaces TypeScript (frontend), execute testes e use type guards para validação.

**P: Posso estender o contrato?**  
R: Mantenha compatibilidade backward. Adicione campos opcionais apenas. Mudanças obrigatórias exigem novo versionamento.

**P: O que fazer se encontrar um problema no contrato?**  
R: Reporte ao Tech Lead. Mudanças no contrato devem ser alinhadas com todas as equipes.

**P: Como testar Telegram localmente?**  
R: Use simulação do update do Telegram ou ferramentas como Postman para simular webhooks.

---

## Suporte

- **Tech Lead**: Decisões sobre evolução do contrato
- **Backend**: Dúvidas sobre Pydantic, validação
- **Frontend**: Dúvidas sobre TypeScript, type guards
- **QA**: Dúvidas sobre testes, casos de teste

---

**Versão**: 1.0  
**Data**: 2024-01-01  
**Última atualização**: 2024-01-01
