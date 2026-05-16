from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Generator

from app.domain.contracts import DocumentCreateRequest
from app.domain.enums import Channel
from app.domain.models import (
    AiLog,
    Attendance,
    DocumentChunk,
    Feedback,
    Handoff,
    KnowledgeDocument,
    MessageRecord,
    ToolCall,
    User,
)
from app.domain.models import RetrievalResult as RetrievalResult


class LLMGateway(ABC):
    @abstractmethod
    def generate(
        self,
        question: str,
        contexts: list[RetrievalResult],
        system_prompt: str | None = None,
    ) -> str:
        ...

    def generate_stream(
        self,
        question: str,
        contexts: list[RetrievalResult],
        system_prompt: str | None = None,
    ) -> Generator[str, None, None]:
        yield self.generate(question, contexts, system_prompt)


class Retriever(ABC):
    @abstractmethod
    def search(self, query: str, top_k: int = 3) -> list[RetrievalResult]:
        ...


class Repository(ABC):
    @abstractmethod
    def seed_default_documents(self) -> None:
        ...

    @abstractmethod
    def find_or_create_user(self, external_id: str, channel: Channel) -> User:
        ...

    @abstractmethod
    def create_attendance(self, user_id: str, channel: Channel) -> Attendance:
        ...

    @abstractmethod
    def mark_attendance_escalated(self, attendance_id: str, reason: str) -> Handoff:
        ...

    @abstractmethod
    def add_message(self, message: MessageRecord) -> MessageRecord:
        ...

    @abstractmethod
    def add_feedback(
        self, message_id: str, useful: bool, comment: str | None
    ) -> Feedback:
        ...

    @abstractmethod
    def add_ai_log(self, log: AiLog) -> AiLog:
        ...

    @abstractmethod
    def add_tool_call(self, tool_call: ToolCall) -> ToolCall:
        ...

    @abstractmethod
    def create_document(self, payload: DocumentCreateRequest) -> KnowledgeDocument:
        ...

    @abstractmethod
    def list_documents(self) -> list[KnowledgeDocument]:
        ...

    @abstractmethod
    def reindex_documents(self) -> tuple[int, int]:
        ...

    @abstractmethod
    def list_active_chunks(self) -> list[DocumentChunk]:
        ...

    @abstractmethod
    def get_document(self, document_id: str) -> KnowledgeDocument | None:
        ...

    @abstractmethod
    def list_attendances(self) -> list[Attendance]:
        ...

    @abstractmethod
    def list_messages_by_attendance(
        self, attendance_id: str
    ) -> list[MessageRecord]:
        ...

    @abstractmethod
    def count_messages_by_attendance(self) -> dict[str, int]:
        ...

    @abstractmethod
    def get_attendance(self, attendance_id: str) -> Attendance | None:
        ...

    @abstractmethod
    def get_feedback_by_message(self, message_id: str) -> list[Feedback]:
        ...

    @abstractmethod
    def metrics_snapshot(self) -> dict[str, object]:
        ...
