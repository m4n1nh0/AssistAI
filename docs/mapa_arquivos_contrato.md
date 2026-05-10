# Mapa de Arquivos — Contrato Oficial de Pergunta e Resposta

## 📍 Localização de Todos os Arquivos do Contrato

### 📄 Documentação (`/docs/`)

| Arquivo | Descrição | Para quem? |
|---------|-----------|-----------|
| [`README_CONTRATO.md`](README_CONTRATO.md) | **COMECE AQUI** — Índice e visão geral completa | Todos |
| [`contrato_pergunta_resposta.md`](contrato_pergunta_resposta.md) | Especificação formal completa do contrato v1.0 | Todos (referência) |
| [`exemplos_contrato.md`](exemplos_contrato.md) | Exemplos práticos em Python, TypeScript e JSON | Developers |
| [`guia_conformidade_contrato.md`](guia_conformidade_contrato.md) | Guia específico por equipe (Backend, Frontend, Telegram, QA) | Cada equipe |
| [`mapa_arquivos_contrato.md`](mapa_arquivos_contrato.md) | Este arquivo — localização de todos os recursos | Todos |

---

### 💻 Backend — Python

| Arquivo | Descrição | Importar | Usar para |
|---------|-----------|----------|----------|
| [`backend/app/domain/contracts.py`](../../backend/app/domain/contracts.py) | **Modelos Pydantic** do contrato (REQUEST, RESPONSE, FEEDBACK) | `from app.domain.contracts import AskRequest, AskResponse` | Definir estrutura de entrada/saída |
| [`backend/app/infrastructure/validation.py`](../../backend/app/infrastructure/validation.py) | **Validadores e Builders** (sanitização, builders de resposta, mapeamento Telegram) | `from app.infrastructure.validation import validate_ask_request, build_success_response` | Validar conformidade, construir respostas |
| [`backend/tests/test_contract.py`](../../backend/tests/test_contract.py) | **Testes de Contrato** (validação, integração) | `pytest backend/tests/test_contract.py` | Testar conformidade com contrato |

**Para Backend:**
```bash
# 1. Importar
from app.domain.contracts import AskRequest, AskResponse
from app.infrastructure.validation import validate_ask_request

# 2. Usar
@router.post("/ask", response_model=AskResponse)
async def ask(request: AskRequest) -> AskResponse:
    validate_ask_request(request)
    ...

# 3. Testar
pytest backend/tests/test_contract.py -v
```

---

### 🎨 Frontend — TypeScript

| Arquivo | Descrição | Importar | Usar para |
|---------|-----------|----------|----------|
| [`frontend/src/domain/contracts.ts`](../../frontend/src/domain/contracts.ts) | **Interfaces TypeScript** (REQUEST, RESPONSE, ERROR) + **Type Guards** | `import { AskRequest, AskResponse, createAskRequest, isAskResponse } from "@/domain/contracts"` | Type-safe communication, validação |

**Para Frontend:**
```typescript
// 1. Importar
import { 
  AskRequest, 
  AskResponse, 
  createAskRequest, 
  isAskResponse 
} from "@/domain/contracts";

// 2. Usar
const request = createAskRequest("Pergunta?", "web", "user123");
const response = await fetch("/api/ask", { body: JSON.stringify(request) });
const data = await response.json();

if (isAskResponse(data)) {
  console.log(data.answer);
  console.log(data.sources);
}

// 3. Testar (Jest)
test("createAskRequest deve gerar request válido", () => {
  const req = createAskRequest("Teste", "web");
  expect(req.version).toBe("1.0");
});
```

---

### 🤖 Integrações — Telegram

| Arquivo | Descrição | Função chave | Usar para |
|---------|-----------|-----------|----------|
| [`backend/app/infrastructure/validation.py`](../../backend/app/infrastructure/validation.py) | Contém `map_telegram_to_ask_request` | `map_telegram_to_ask_request(update, user_id)` | Mapear update do Telegram → AskRequest |

**Para Telegram:**
```python
from app.infrastructure.validation import map_telegram_to_ask_request

# Webhook recebe update
update = { "message": { "text": "Olá", "message_id": 123 } }

# Mapear para contrato
request = map_telegram_to_ask_request(update, user_id="tg_user")

# Processar como qualquer outro request
response = await ask_service.process(request)
```

---

## 🗂️ Estrutura Visual

```
AssistAI/
├── docs/
│   ├── README_CONTRATO.md ⭐ (COMECE AQUI)
│   ├── contrato_pergunta_resposta.md (Especificação)
│   ├── exemplos_contrato.md (Exemplos)
│   ├── guia_conformidade_contrato.md (Por equipe)
│   ├── mapa_arquivos_contrato.md (Este arquivo)
│   └── ... (outros docs)
│
├── backend/
│   ├── app/
│   │   ├── domain/
│   │   │   ├── contracts.py ⭐ (Modelos Pydantic)
│   │   │   ├── enums.py
│   │   │   └── models.py
│   │   ├── infrastructure/
│   │   │   ├── validation.py ⭐ (Validadores)
│   │   │   └── ...
│   │   ├── api/
│   │   │   ├── routes/
│   │   │   │   └── ask.py (Endpoint /ask)
│   │   │   └── ...
│   │   └── ...
│   ├── tests/
│   │   ├── test_contract.py ⭐ (Testes)
│   │   └── ...
│   └── ...
│
├── frontend/
│   ├── src/
│   │   ├── domain/
│   │   │   ├── contracts.ts ⭐ (Interfaces TypeScript)
│   │   │   └── ...
│   │   ├── application/
│   │   │   ├── hooks/
│   │   │   │   └── useChat.ts (Hook de chat)
│   │   │   └── ...
│   │   ├── presentation/
│   │   │   ├── components/
│   │   │   │   └── ChatPage.tsx
│   │   │   └── ...
│   │   └── ...
│   └── ...
│
└── ... (outros diretórios)
```

---

## 🎯 Por onde começar? (Guia Rápido)

### Sou do Backend (Python/FastAPI)?
1. Leia: [`README_CONTRATO.md`](README_CONTRATO.md)
2. Consulte: [`backend/app/domain/contracts.py`](../../backend/app/domain/contracts.py)
3. Implemente: Seguindo [`guia_conformidade_contrato.md`](guia_conformidade_contrato.md) - Seção Backend
4. Teste: Execute `pytest backend/tests/test_contract.py`

### Sou do Frontend (TypeScript/React)?
1. Leia: [`README_CONTRATO.md`](README_CONTRATO.md)
2. Consulte: [`frontend/src/domain/contracts.ts`](../../frontend/src/domain/contracts.ts)
3. Implemente: Seguindo [`guia_conformidade_contrato.md`](guia_conformidade_contrato.md) - Seção Frontend
4. Use: Type guards com `isAskResponse()`, `isErrorResponse()`

### Sou do Telegram (Integrações)?
1. Leia: [`README_CONTRATO.md`](README_CONTRATO.md)
2. Consulte: [`guia_conformidade_contrato.md`](guia_conformidade_contrato.md) - Seção Telegram
3. Use: `map_telegram_to_ask_request()` de `validation.py`
4. Mapeie: Update do Telegram → AskRequest

### Sou de QA (Testes)?
1. Leia: [`README_CONTRATO.md`](README_CONTRATO.md)
2. Consulte: [`backend/tests/test_contract.py`](../../backend/tests/test_contract.py)
3. Execute: `pytest backend/tests/test_contract.py -v`
4. Implemente: Casos de teste seguindo [`guia_conformidade_contrato.md`](guia_conformidade_contrato.md) - Seção QA

---

## 🔗 Referências Cruzadas

### AskRequest (Entrada)
- **Especificação**: [`contrato_pergunta_resposta.md`](contrato_pergunta_resposta.md#entrada-request)
- **Modelo Pydantic**: [`contracts.py`](../../backend/app/domain/contracts.py) - `class AskRequest`
- **Interface TypeScript**: [`contracts.ts`](../../frontend/src/domain/contracts.ts) - `interface AskRequest`
- **Exemplos**: [`exemplos_contrato.md`](exemplos_contrato.md#python-backend---pydantic)
- **Validação**: [`validation.py`](../../backend/app/infrastructure/validation.py) - `validate_ask_request()`

### AskResponse (Saída)
- **Especificação**: [`contrato_pergunta_resposta.md`](contrato_pergunta_resposta.md#saída-response)
- **Modelo Pydantic**: [`contracts.py`](../../backend/app/domain/contracts.py) - `class AskResponse`
- **Interface TypeScript**: [`contracts.ts`](../../frontend/src/domain/contracts.ts) - `interface AskResponse`
- **Exemplos**: [`exemplos_contrato.md`](exemplos_contrato.md#exemplo-de-response-de-sucesso)
- **Builders**: [`validation.py`](../../backend/app/infrastructure/validation.py) - `build_success_response()`, `build_fallback_response()`
- **Type Guard**: [`contracts.ts`](../../frontend/src/domain/contracts.ts) - `isAskResponse()`

### Integração Telegram
- **Especificação**: [`contrato_pergunta_resposta.md`](contrato_pergunta_resposta.md#integração-por-canal)
- **Mapeamento**: [`validation.py`](../../backend/app/infrastructure/validation.py) - `map_telegram_to_ask_request()`
- **Exemplo**: [`guia_conformidade_contrato.md`](guia_conformidade_contrato.md#1-webhook-receiver)

### Testes
- **Testes de Contrato**: [`backend/tests/test_contract.py`](../../backend/tests/test_contract.py)
- **Guia de Testes**: [`exemplos_contrato.md`](exemplos_contrato.md#testes-unitários)
- **Casos de Teste**: [`guia_conformidade_contrato.md`](guia_conformidade_contrato.md#1-casos-de-teste-de-contrato)

---

## 📊 Checklist de Conformidade

### Antes de fazer um PR, verifique:

```
Backend:
- [ ] Usado modelos Pydantic de contracts.py
- [ ] validate_ask_request() chamado
- [ ] Resposta construída com build_success_response()
- [ ] Testes em test_contract.py passando

Frontend:
- [ ] Usado interfaces TypeScript de contracts.ts
- [ ] createAskRequest() usado para criar requests
- [ ] isAskResponse() e isErrorResponse() usados
- [ ] Type checking sem erros (typescript strict)

Telegram:
- [ ] map_telegram_to_ask_request() usado
- [ ] Response enviada corretamente
- [ ] Fallback tratado

QA:
- [ ] pytest backend/tests/test_contract.py -v ✓
- [ ] Casos de teste de entrada ✓
- [ ] Casos de teste de saída ✓
- [ ] Integração Web ✓
- [ ] Integração Telegram ✓
```

---

## 🆘 Problemas Comuns

| Problema | Solução |
|----------|---------|
| "Erro ao validar AskRequest" | Verifique se `question` tem 1-1000 chars e `channel` é "web" ou "telegram" |
| "Type 'AskResponse' has no property 'x'" | Use `isAskResponse()` type guard antes de acessar |
| "Telegram não mapeia corretamente" | Verifique `map_telegram_to_ask_request()` em `validation.py` |
| "Teste de contrato falha" | Execute `pytest backend/tests/test_contract.py -v` para detalhes |

---

## 📞 Suporte

- **Dúvidas sobre especificação**: Leia [`contrato_pergunta_resposta.md`](contrato_pergunta_resposta.md)
- **Dúvidas sobre implementação**: Veja [`exemplos_contrato.md`](exemplos_contrato.md)
- **Dúvidas específicas de equipe**: Consulte [`guia_conformidade_contrato.md`](guia_conformidade_contrato.md)
- **Dúvidas sobre code**: Abra PR ou converse com Tech Lead

---

**Versão**: 1.0  
**Data**: 2024-01-01  
**Última atualização**: 2024-01-01  
**Mantido por**: Tech Lead / Arquitetura
