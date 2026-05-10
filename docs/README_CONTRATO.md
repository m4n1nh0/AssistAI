# Contrato Oficial de Pergunta e Resposta — Índice Completo

## 📋 Resumo

O **Contrato Oficial de Pergunta e Resposta** é o padrão unificado para comunicação entre Web, Telegram, API e Motor de IA do Assistente Inteligente. Versão **1.0**.

**Objetivo**: Padronizar, evitar retrabalho e garantir consistência entre equipes.

---

## 📚 Documentação Completa

### 1. **Especificação Formal** 
   📄 [`docs/contrato_pergunta_resposta.md`](contrato_pergunta_resposta.md)
   - Estrutura JSON completa
   - Campos obrigatórios e opcionais
   - Validações e regras
   - Mensagens de erro padronizadas
   - Fallback e regras de ativação

### 2. **Exemplos Práticos**
   📄 [`docs/exemplos_contrato.md`](exemplos_contrato.md)
   - Exemplos Python (Pydantic)
   - Exemplos TypeScript (React)
   - Exemplos JSON bruto
   - Integração FastAPI
   - Testes Pytest e Jest

### 3. **Guia de Conformidade (Para cada equipe)**
   📄 [`docs/guia_conformidade_contrato.md`](guia_conformidade_contrato.md)
   - Backend (FastAPI + Pydantic)
   - Frontend (React + TypeScript)
   - Telegram (Integrações)
   - QA (Testes)
   - Checklists e validação local

---

## 💻 Implementação (Código)

### Backend (Python - FastAPI)

| Arquivo | Descrição |
|---------|-----------|
| [`backend/app/domain/contracts.py`](../backend/app/domain/contracts.py) | Modelos Pydantic do contrato (REQUEST, RESPONSE, FEEDBACK, etc.) |
| [`backend/app/infrastructure/validation.py`](../backend/app/infrastructure/validation.py) | Validadores, sanitização, builders de resposta |
| [`backend/tests/test_contract.py`](../backend/tests/test_contract.py) | Testes de conformidade com o contrato |

**Usar:**
```python
from app.domain.contracts import AskRequest, AskResponse
from app.infrastructure.validation import validate_ask_request, build_success_response
```

### Frontend (TypeScript - React)

| Arquivo | Descrição |
|---------|-----------|
| [`frontend/src/domain/contracts.ts`](../frontend/src/domain/contracts.ts) | Interfaces TypeScript do contrato + type guards |

**Usar:**
```typescript
import { AskRequest, AskResponse, createAskRequest, isAskResponse } from "@/domain/contracts";
```

---

## 🎯 Estrutura Rápida do Contrato

### REQUEST (Entrada)

```json
{
  "version": "1.0",
  "question": "string (1-1000 chars, obrigatório)",
  "user_id": "string (opcional)",
  "channel": "web|telegram (obrigatório)",
  "conversation_id": "string (opcional)",
  "metadata": {
    "timestamp": "ISO 8601 (obrigatório)",
    "user_agent": "string (opcional)",
    "ip_address": "string (opcional)",
    "message_id": "string (Telegram, opcional)"
  }
}
```

### RESPONSE (Saída - Sucesso)

```json
{
  "version": "1.0",
  "answer": "string (max 4000 chars)",
  "sources": [
    {
      "document_id": "string",
      "title": "string",
      "content": "string",
      "score": 0.0-1.0,
      "version": "string"
    }
  ],
  "score": 0.0-1.0,
  "fallback": false,
  "conversation_id": "string (opcional)",
  "metadata": {
    "processing_time_ms": number,
    "model_used": "gpt-4|fallback",
    "timestamp": "ISO 8601"
  }
}
```

### RESPONSE (Saída - Erro)

```json
{
  "version": "1.0",
  "error": {
    "code": "INVALID_REQUEST|QUESTION_TOO_LONG|UNSUPPORTED_CHANNEL|SERVICE_UNAVAILABLE|INTERNAL_ERROR|RATE_LIMIT_EXCEEDED",
    "message": "string",
    "details": { "field": "string", "message": "string" }
  }
}
```

---

## 🚀 Quick Start

### Backend (FastAPI)

1. **Importar modelos:**
   ```python
   from app.domain.contracts import AskRequest, AskResponse
   from app.infrastructure.validation import validate_ask_request, build_success_response
   ```

2. **Criar endpoint:**
   ```python
   @router.post("/ask", response_model=AskResponse)
   async def ask(request: AskRequest) -> AskResponse:
       validate_ask_request(request)
       # ... processar ...
       return build_success_response(...)
   ```

3. **Testar:**
   ```bash
   pytest backend/tests/test_contract.py -v
   ```

### Frontend (TypeScript)

1. **Importar tipos:**
   ```typescript
   import { AskRequest, AskResponse, createAskRequest, isAskResponse } from "@/domain/contracts";
   ```

2. **Criar request:**
   ```typescript
   const request = createAskRequest("Como?", "web", "user123");
   ```

3. **Enviar e validar:**
   ```typescript
   const response = await fetch("/api/ask", {
     method: "POST",
     body: JSON.stringify(request),
   });
   const data = await response.json();
   if (isAskResponse(data)) { /* use resposta */ }
   ```

---

## ✅ Checklist de Implementação

### Backend
- [ ] Modelos Pydantic em `contracts.py`
- [ ] Validadores em `validation.py`
- [ ] Endpoint `/ask` retorna `AskResponse`
- [ ] Testes em `test_contract.py` passando
- [ ] Auditoria implementada
- [ ] Rate limiting implementado

### Frontend
- [ ] Interfaces TypeScript em `contracts.ts`
- [ ] Type guards implementados
- [ ] Hook de chat usa modelos
- [ ] Componentes exibem resposta/fontes/fallback
- [ ] Erros tratados corretamente

### Telegram
- [ ] Webhook recebe updates
- [ ] `map_telegram_to_ask_request` usado
- [ ] Response enviada ao Telegram
- [ ] Fallback tratado

### QA
- [ ] Testes de contrato executados
- [ ] Casos de teste de entrada e saída
- [ ] Integração Web testada
- [ ] Integração Telegram testada
- [ ] Auditoria verificada

---

## 📊 Validação com curl

```bash
# Request válido
curl -X POST http://localhost:8000/api/ask \
  -H "Content-Type: application/json" \
  -d '{
    "version": "1.0",
    "question": "Teste",
    "channel": "web",
    "metadata": {"timestamp": "2024-01-01T12:00:00Z"}
  }'

# Esperado: HTTP 200 + AskResponse JSON
```

---

## 📞 Referências e Suporte

| Equipe | Responsável | Referência |
|--------|-------------|-----------|
| Backend | Implementar FastAPI + Pydantic | [`guia_conformidade_contrato.md`](guia_conformidade_contrato.md) - Seção Backend |
| Frontend | Implementar React + TypeScript | [`guia_conformidade_contrato.md`](guia_conformidade_contrato.md) - Seção Frontend |
| Telegram | Mapear updates → AskRequest | [`guia_conformidade_contrato.md`](guia_conformidade_contrato.md) - Seção Telegram |
| QA | Testes e validação | [`guia_conformidade_contrato.md`](guia_conformidade_contrato.md) - Seção QA |
| Tech Lead | Evolução do contrato | Contato direto |

---

## 🔄 Fluxo Completo

```
1. Web/Telegram envia AskRequest conforme contrato
   ↓
2. Backend valida automaticamente com Pydantic
   ↓
3. Backend processa (RAG, LLM, etc.)
   ↓
4. Backend constrói AskResponse conforme contrato
   ↓
5. Frontend recebe e valida com type guards
   ↓
6. Frontend exibe resposta, fontes, fallback
   ↓
7. Usuário envia feedback (opcional)
   ↓
8. Tudo é auditado e logado
```

---

## 📌 Importante

- **Versão**: 1.0 (atual)
- **Compatibilidade**: Backward-compatible
- **Evolução**: Mudanças exigem consenso de todas as equipes
- **Testes**: Execute antes de cada PR

---

## 🎓 Leitura Recomendada (em ordem)

1. Este arquivo (visão geral)
2. [`contrato_pergunta_resposta.md`](contrato_pergunta_resposta.md) (especificação)
3. [`exemplos_contrato.md`](exemplos_contrato.md) (exemplos)
4. [`guia_conformidade_contrato.md`](guia_conformidade_contrato.md) (sua equipe)
5. Código correspondente (`contracts.py` ou `contracts.ts`)
6. Testes (`test_contract.py`)

---

## 📝 Versionamento do Contrato

| Versão | Data | Mudanças |
|--------|------|----------|
| 1.0 | 2024-01-01 | Versão inicial |

**Próximas versões**: Serão comunicadas com antecedência para garantir transição suave.

---

**Última atualização**: 2024-01-01  
**Mantido por**: Tech Lead / Arquitetura
