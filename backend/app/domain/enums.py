from enum import StrEnum


class Channel(StrEnum):
    WEB = "web"
    TELEGRAM = "telegram"


class DocumentStatus(StrEnum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    DRAFT = "draft"


class Intent(StrEnum):
    GREETING = "saudacao"
    PROCEDURE = "procedimento"
    HUMAN_REQUEST = "solicitacao_humana"
    HUMAN = "solicitacao_humana"
    TICKET_STATUS = "consulta_chamado"
    OUT_OF_SCOPE = "fora_de_escopo"
    UNKNOWN = "desconhecida"

