from app.domain.models import Intent


def classify_intent(message: str) -> tuple[Intent, float]:
    normalized = message.lower()

    if any(term in normalized for term in ["oi", "ola", "olá", "bom dia", "boa tarde"]):
        return Intent.GREETING, 0.92
    if any(term in normalized for term in ["humano", "atendente", "pessoa", "suporte humano"]):
        return Intent.HUMAN, 0.9
    if any(term in normalized for term in ["status", "chm-", "chamado"]):
        if "status" in normalized or "chm-" in normalized:
            return Intent.TICKET_STATUS, 0.86
        return Intent.PROCEDURE, 0.78
    if any(term in normalized for term in ["senha", "acesso", "prioridade", "abrir", "portal"]):
        return Intent.PROCEDURE, 0.8

    return Intent.OUT_OF_SCOPE, 0.42
