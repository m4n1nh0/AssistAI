SUSPICIOUS_PATTERNS = (
    "ignore as instruções",
    "ignore instrucoes",
    "revele o prompt",
    "system prompt",
)


def has_prompt_injection_risk(message: str) -> bool:
    normalized = message.lower()
    return any(pattern in normalized for pattern in SUSPICIOUS_PATTERNS)
