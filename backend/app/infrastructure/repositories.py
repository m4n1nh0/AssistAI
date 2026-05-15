from uuid import uuid4

from app.domain.models import Attendance, Channel, KnowledgeDocument, MessageRecord


class InMemoryRepository:
    def __init__(self) -> None:
        self.attendances: dict[str, Attendance] = {}
        self.feedbacks: list[dict] = []
        self.documents: dict[str, KnowledgeDocument] = {}

    def get_or_create_attendance(self, user_id: str, channel: Channel) -> Attendance:
        for attendance in self.attendances.values():
            if attendance.user_id == user_id and attendance.channel == channel and not attendance.needs_human:
                return attendance

        attendance = Attendance(id=f"att-{uuid4().hex[:8]}", user_id=user_id, channel=channel)
        self.attendances[attendance.id] = attendance
        return attendance

    def add_message(self, attendance: Attendance, message: MessageRecord) -> MessageRecord:
        attendance.messages.append(message)
        return message

    def mark_handoff(self, attendance: Attendance) -> None:
        attendance.needs_human = True

    def add_feedback(self, message_id: str, useful: bool, comment: str | None) -> None:
        self.feedbacks.append({"message_id": message_id, "useful": useful, "comment": comment})

    def list_attendances(self) -> list[Attendance]:
        return list(self.attendances.values())

    def get_attendance(self, attendance_id: str) -> Attendance | None:
        return self.attendances.get(attendance_id)

    def add_document(self, document: KnowledgeDocument) -> KnowledgeDocument:
        self.documents[document.id] = document
        return document

    def list_documents(self) -> list[KnowledgeDocument]:
        return list(self.documents.values())


repository = InMemoryRepository()
