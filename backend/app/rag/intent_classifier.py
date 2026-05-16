from app.domain.enums import Intent


class IntentClassifier:
    def classify(self, message: str) -> tuple[Intent, float]:
        normalized = message.lower()
        if any(term in normalized for term in ["oi", "olá", "ola", "bom dia", "boa tarde", "boa noite"]):
            return Intent.GREETING, 0.8
        if any(term in normalized for term in ["humano", "atendente", "pessoa", "suporte humano"]):
            return Intent.HUMAN_REQUEST, 0.9
        if any(term in normalized for term in ["chamado", "senha", "acesso", "perfil", "erro"]):
            return Intent.PROCEDURE, 0.75
        return Intent.UNKNOWN, 0.45
