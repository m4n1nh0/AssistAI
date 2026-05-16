from enum import StrEnum


class Channel(StrEnum):
    WEB = "web"
    TELEGRAM = "telegram"


class Intent(StrEnum):
    GREETING = "saudacao"
    PROCEDURE = "procedimento"
    HUMAN_REQUEST = "solicitacao_humana"
    OUT_OF_SCOPE = "fora_de_escopo"
    UNKNOWN = "desconhecida"


class DocumentStatus(StrEnum):
    DRAFT = "draft"
    ACTIVE = "active"
    INACTIVE = "inactive"
