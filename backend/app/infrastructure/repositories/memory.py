from app.domain.entities import Attendance, KnowledgeDocument, Message


class InMemoryStore:
    def __init__(self) -> None:
        self.attendances: dict[str, Attendance] = {}
        self.messages: dict[str, Message] = {}
        self.documents: dict[str, KnowledgeDocument] = {}
        self.feedbacks: dict[str, dict[str, object]] = {}


store = InMemoryStore()
