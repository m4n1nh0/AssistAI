# Análise Crítica e Revisão do Contrato Oficial v1.0

## Resumo Executivo

O contrato foi bem estruturado como base, mas há **11 inconsistências críticas** e **8 falhas de integração** que podem gerar retrabalho significativo. Este documento lista cada problema, seu impacto e a solução recomendada.

**Status**: ⚠️ Necessita revisão antes da implementação final

---

## 🔴 PROBLEMAS CRÍTICOS (Bloqueadores)

### 1. **PROBLEMA: Mismatch entre Python e TypeScript em Namespacing**

**Onde**: 
- Python: `class SourceResponse` em `backend/app/domain/contracts.py`
- TypeScript: `interface Source` em `frontend/src/domain/contracts.ts`

**Impacto**: Frontend espera `Source`, backend envia `SourceResponse` → Serialização quebra

**Solução**:
```typescript
// TypeScript deve ser
export interface SourceResponse {  // Renomear para SourceResponse
  document_id: string;
  title: string;
  content: string;
  score: number;
  version: string;
}
```

**Ação necessária**: 
- [ ] Renomear `Source` para `SourceResponse` em `contracts.ts`
- [ ] Atualizar factory e type guards

---

### 2. **PROBLEMA: Serialização de Timestamps (datetime → string)**

**Onde**:
- Python: `timestamp: datetime` (objeto datetime)
- TypeScript: `timestamp: string` (ISO 8601)
- JSON: string sempre

**Impacto**: 
- Backend envia datetime object que serializa para ISO 8601 ✓
- Frontend recebe string ✓
- **MAS**: Frontend tentará usar string como Date() sem parsear explicitamente
- **E**: Backend recebe JSON string, não datetime

**Problema adicional**: `ResponseMetadata.timestamp` e `RequestMetadata.timestamp` são datetime em Python mas string no JSON

**Solução**:

```python
# backend/app/domain/contracts.py - Adicionar config JSON
class RequestMetadata(BaseModel):
    timestamp: datetime = Field(...)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }
        
# OU usar datetime parsing automático
@validator("timestamp", pre=True)
def parse_timestamp(cls, v):
    if isinstance(v, str):
        return datetime.fromisoformat(v.replace("Z", "+00:00"))
    return v
```

**Ação necessária**:
- [ ] Adicionar validadores para parsear ISO 8601 strings em Python
- [ ] Adicionar helper `parseTimestamp()` em TypeScript
- [ ] Documentar claramente que JSON sempre usa ISO 8601 strings

---

### 3. **PROBLEMA: Enum/Type Mismatch para FallbackReason e ErrorCode**

**Onde**:
- Python: `class FallbackReason(str)` (classe Enum)
- TypeScript: `type FallbackReason = "low_score" | ...` (union type)

**Impacto**: 
- Python pode usar `FallbackReason.LOW_SCORE` (object)
- TypeScript pode usar `"low_score"` (string literal)
- JSON sempre string ✓
- **MAS**: Backend enviando `FallbackReason.LOW_SCORE` serializa para `"low_score"` ✓
- **E**: Frontend type checks contra type union ✓

**Observação**: Funciona, mas é inconsistente mentalmente. Melhor manter Enums em ambos.

**Solução recomendada**:
```python
# Python - manter como string Literal é mais flexível
from typing import Literal

FallbackReason = Literal["low_score", "no_sources", "error", "intent_out_of_scope", "service_unavailable"]
```

**Ação necessária**:
- [ ] Decidir: usar `Enum` em ambos ou `Literal` em ambos
- [ ] Se usar `Enum` em Python, garantir serialização para string no JSON

---

### 4. **PROBLEMA: Sincronização de Versão do Contrato**

**Onde**: 
- Ambos têm `version: str = "1.0"` com default

**Impacto**: 
- Se versão mudar, deve mudar em ambos os lugares
- Sem guardrail automático
- **Risco**: Frontend envia v2, backend espera v1

**Solução**:
```python
# backend/app/domain/contracts.py
CONTRACT_VERSION = "1.0"

class AskRequest(BaseModel):
    version: str = Field(default=CONTRACT_VERSION, ...)
    
    @validator("version")
    def validate_version(cls, v):
        if v != CONTRACT_VERSION:
            raise ValueError(f"Versão não suportada: {v}. Esperado: {CONTRACT_VERSION}")
        return v
```

```typescript
// frontend/src/domain/contracts.ts
export const CONTRACT_VERSION = "1.0";

export function createAskRequest(...): AskRequest {
  return {
    version: CONTRACT_VERSION,
    ...
  };
}
```

**Ação necessária**:
- [ ] Extrair `CONTRACT_VERSION` como constante em ambos
- [ ] Atualizar factory e validadores

---

### 5. **PROBLEMA: Campos Extras em DocumentCreateRequest não Sincronizados**

**Onde**:
- Python tem `DocumentCreateRequest` com 10 campos (category, channel, source, owner, sensitivity, tags)
- TypeScript não tem equivalente
- Especificação (MD) não documenta esses campos

**Impacto**: 
- Equipe de Frontend não sabe que deve enviar esses campos
- Equipe de Backend espera, Frontend não envia
- Integração quebra para upload de documentos

**Exemplo problema**:
```python
# Backend espera
{
  "title": "...",
  "category": "...",      # <- Frontend não sabe!
  "channel": "both",      # <- Frontend não sabe!
  "source": "manual",     # <- Frontend não sabe!
  "owner": "suporte",     # <- Frontend não sabe!
  "sensitivity": "interno", # <- Frontend não sabe!
  "content": "...",
  "tags": ["..."]         # <- Frontend não sabe!
}
```

**Solução**:
```typescript
// frontend/src/domain/contracts.ts - Adicionar
export interface DocumentCreateRequest {
  title: string;
  category: string;
  channel?: string;
  version?: string;
  status?: DocumentStatus;
  source?: string;
  owner?: string;
  sensitivity?: string;
  content: string;
  tags?: string[];
}
```

**Ação necessária**:
- [ ] Adicionar `DocumentCreateRequest` em TypeScript
- [ ] Documentar campos em `contrato_pergunta_resposta.md`
- [ ] Sincronizar com AskRequest/AskResponse ou documentar claramente que é separado

---

## 🟡 PROBLEMAS SECUNDÁRIOS (Alto Impacto)

### 6. **PROBLEMA: MessageResponse e AttendanceDetailResponse Não Documentados**

**Onde**:
- Python tem `MessageResponse` e `AttendanceDetailResponse` em `contracts.py`
- Não aparecem no MD de especificação
- Não aparecem em TypeScript

**Impacto**: 
- Histório e atendimentos: equipes não sabem a estrutura esperada
- S2-06 (persistir histórico): sem contrato claro
- S2-07 (tela de chat): sem tipo

**Campos problemáticos**: 
- `MessageResponse` tem `intent` e `confidence` que não estão em `AskResponse`
- Como isso se relaciona com fallback e score?

**Solução**:
```typescript
// frontend/src/domain/contracts.ts - Adicionar
export interface MessageResponse {
  message_id: string;
  user_message: string;
  assistant_answer: string;
  fallback: boolean;
  intent: Intent;
  confidence: number;
  sources: SourceResponse[];
  created_at: string;
}

export interface AttendanceDetailResponse {
  attendance_id: string;
  user_id: string;
  channel: Channel;
  escalated: boolean;
  started_at: string;
  messages: MessageResponse[];
}
```

**Ação necessária**:
- [ ] Adicionar `MessageResponse` e `AttendanceDetailResponse` em `contrato_pergunta_resposta.md`
- [ ] Sincronizar com TypeScript
- [ ] Esclarecer: `confidence` é igual a `score` de `AskResponse`?

---

### 7. **PROBLEMA: Rate Limiting Documentado mas Não Implementado**

**Onde**:
- Especificação diz: "Rate limiting: Máximo 10 requisições por minuto por user_id"
- `validation.py` não tem função de rate limiting
- Backend não tem middleware de rate limiting

**Impacto**: 
- Sem proteção contra DoS no dia 1 da POC
- Equipe de Backend precisa implementar
- Sem contrato claro (estratégia, headers de resposta, etc.)

**Solução**:
```python
# backend/app/infrastructure/validation.py - Adicionar
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

# Em router
@limiter.limit("10/minute")
@router.post("/ask")
async def ask(request: AskRequest):
    ...
```

**Ação necessária**:
- [ ] Documentar estratégia de rate limiting no contrato (por user_id vs. por IP)
- [ ] Implementar no backend com headers de resposta (X-RateLimit-*)
- [ ] Documentar comportamento em ErrorResponse quando limite excedido

---

### 8. **PROBLEMA: Validação de Entrada Incompleta**

**Onde**:
- `validate_ask_request()` valida versão, question, channel, metadata
- **MAS**: não valida user_id, session_id, conversation_id

**Impacto**:
- user_id pode ter caracteres inválidos → quebra auditoria
- session_id pode ser muito longo → problema de storage
- conversation_id pode ser duplicado entre usuários

**Solução**:
```python
# backend/app/infrastructure/validation.py - Enhance
def validate_ask_request(request: AskRequest) -> None:
    # ... código existente ...
    
    # Validar user_id
    if request.user_id:
        if len(request.user_id) > 255:
            raise ValueError("user_id excede 255 caracteres")
        if not re.match(r"^[\w\-@.]+$", request.user_id):
            raise ValueError("user_id contém caracteres inválidos")
    
    # Validar session_id
    if request.session_id and len(request.session_id) > 255:
        raise ValueError("session_id excede 255 caracteres")
    
    # Validar conversation_id
    if request.conversation_id and len(request.conversation_id) > 255:
        raise ValueError("conversation_id excede 255 caracteres")
```

**Ação necessária**:
- [ ] Estender validação para todos os campos
- [ ] Documentar regras de validação em contrato

---

### 9. **PROBLEMA: Falta de Campo de Rastreamento de Request**

**Onde**:
- Request não tem ID único
- Response não referencia ID do request

**Impacto**:
- Auditoria não consegue correlacionar request → response
- Logs desconectados
- Debugging difícil

**Solução**:
```python
# Adicionar ao contrato
class AskRequest(BaseModel):
    version: str
    question: str
    user_id: Optional[str]
    channel: Channel
    request_id: Optional[str] = Field(default_factory=lambda: str(uuid.uuid4()))  # NOVO
    # ... resto ...

class AskResponse(BaseModel):
    version: str
    answer: str
    request_id: Optional[str]  # NOVO - referencia ao request
    # ... resto ...
```

**Ação necessária**:
- [ ] Adicionar `request_id` em AskRequest (gerado no frontend ou backend)
- [ ] Adicionar `request_id` em AskResponse (retorna o mesmo do request)
- [ ] Usar para correlação em logs

---

### 10. **PROBLEMA: Sem Contrato para Serviços Auxiliares**

**Onde**:
- Existe `FeedbackRequest`, `AttendanceListItem`, `DocumentSummary`
- **MAS**: sem contrato para endpoints de listar (GET /attendances, GET /documents)
- Sem paginação definida
- Sem filtros definidos

**Impacto**:
- Frontend não sabe como listar atendimentos
- Backend pode não retornar paginação
- S4 (base administrável): sem contrato claro

**Solução**:
```python
# Adicionar ao contrato
class PaginatedResponse(BaseModel):
    """Resposta paginada genérica."""
    items: list[T]  # Generic
    total: int
    page: int
    page_size: int
    has_more: bool

# Usar em endpoints
class AttendanceListResponse(PaginatedResponse):
    items: list[AttendanceListItem]
```

**Ação necessária**:
- [ ] Definir padrão de paginação no contrato
- [ ] Definir filtros padrão (date range, status, etc.)
- [ ] Sincronizar entre Python e TypeScript

---

## 🟠 MELHORIAS RECOMENDADAS (Médio Impacto)

### 11. **MELHORIA: Adicionar Logging Estruturado ao Contrato**

**Sugestão**: Enquanto `validation.py` tem `log_request_contract()` e `log_response_contract()`, não há estrutura clara para logs ao longo do fluxo.

**Solução**:
```python
# Adicionar ao contrato
class AuditLog(BaseModel):
    """Registro de auditoria padronizado."""
    timestamp: datetime
    event_type: str  # "request_received", "response_sent", "fallback_triggered"
    request_id: str
    user_id: Optional[str]
    channel: Channel
    details: dict  # event-specific data
```

---

## 📋 CHECKLIST DE CORREÇÃO

### Correções Prioritárias (Esta Sprint)

```
CRÍTICOS (Bloqueadores S1):
[ ] Renomear Source → SourceResponse em TypeScript
[ ] Adicionar validação de timestamp (ISO 8601 parsing)
[ ] Definir estratégia de Enum vs. Literal
[ ] Extrair CONTRACT_VERSION como constante
[ ] Adicionar DocumentCreateRequest em TypeScript
[ ] Documentar MessageResponse e AttendanceDetailResponse

ALTOS (Impactam S1-S2):
[ ] Implementar rate limiting com estratégia clara
[ ] Estender validação de entrada (user_id, session_id, etc.)
[ ] Adicionar request_id para correlação
[ ] Definir padrão de paginação

MÉDIOS (Importante para S4):
[ ] Definir contrato para GET endpoints
[ ] Adicionar AuditLog ao contrato
```

---

## 📊 Resumo de Inconsistências

| # | Problema | Severidade | Arquivo Python | Arquivo TypeScript | Especificação MD |
|---|----------|-----------|---|---|---|
| 1 | Namespacing (Source vs SourceResponse) | 🔴 | SourceResponse | Source | (indiferente) |
| 2 | Serialização de timestamps | 🔴 | datetime | string | string |
| 3 | Enum vs Literal | 🔴 | class | type | não definido |
| 4 | Versionamento do Contrato | 🔴 | "1.0" | "1.0" | duplicado |
| 5 | DocumentCreateRequest | 🔴 | ✓ | ✗ | ✗ |
| 6 | MessageResponse/AttendanceDetailResponse | 🟡 | ✓ | ✗ | ✗ |
| 7 | Rate Limiting | 🟡 | MD sim, código não | - | ✓ |
| 8 | Validação Incompleta | 🟡 | Parcial | N/A | Incompleta |
| 9 | Request ID Tracking | 🟡 | ✗ | ✗ | ✗ |
| 10 | Contrato para GET/Paginação | 🟡 | ✗ | ✗ | ✗ |
| 11 | Logging Estruturado | 🟠 | Funções soltas | N/A | ✗ |

---

## 🎯 Impacto por Equipe

### Backend
- Sincronizar `DocumentCreateRequest` com TS
- Implementar rate limiting
- Adicionar request ID tracking
- Definir paginação

### Frontend
- Renomear `Source` → `SourceResponse`
- Adicionar `DocumentCreateRequest`
- Adicionar `MessageResponse`, `AttendanceDetailResponse`
- Adicionar helper de timestamp parsing
- Atualizar type guards

### QA
- Testar rate limiting
- Testar validação de timestamp
- Testar correlação com request_id

### Tech Lead
- Decidir estratégia de Enum vs Literal
- Definir paginação padrão
- Revisar e aprovar correções

---

## 📝 Próximas Ações

1. **Hoje**: Circule este documento para revisão com Tech Lead
2. **Amanhã**: Reunião rápida (15min) para decidir estratégias (Enum, paginação, rate limiting)
3. **Depois**: Implementar correções críticas antes de S1-02
4. **Antes de S1-11**: Testes de contrato cobrindo todos os casos

---

## 🔗 Referências

- Contrato: [`docs/contrato_pergunta_resposta.md`](contrato_pergunta_resposta.md)
- Backend: [`backend/app/domain/contracts.py`](../backend/app/domain/contracts.py)
- Frontend: [`frontend/src/domain/contracts.ts`](../frontend/src/domain/contracts.ts)
- Validadores: [`backend/app/infrastructure/validation.py`](../backend/app/infrastructure/validation.py)

---

**Versão**: 1.0  
**Data**: 2024-01-01  
**Severidade Geral**: 🔴 **Necessita Revisão Crítica antes de S1-02**
