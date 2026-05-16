def sanitize_user_message(message: str) -> str:
    return " ".join(message.strip().split())
