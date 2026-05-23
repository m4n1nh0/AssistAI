import json
import dataclasses
from sqlalchemy.orm import Session

from app.domain.enums import Channel
from app.domain.models import AiLog, Attendance, Feedback, MessageRecord, User, KnowledgeDocument, DocumentChunk, new_id
from app.infrastructure.database.models import (
    AiLogModel,
    AttendanceModel,
    FeedbackModel,
    MessageRecordModel,
    UserModel,
)

class MySQLRepository:
    def __init__(self, db_session: Session) -> None:
        self.db = db_session

    def find_or_create_user(self, external_id: str, channel: Channel) -> User:
        user_model = self.db.query(UserModel).filter(UserModel.external_id == external_id).first()
        if not user_model:
            user_model = UserModel(
                id=new_id("usr"),
                external_id=external_id,
                channel=channel.value
            )
            self.db.add(user_model)
            self.db.commit()
            self.db.refresh(user_model)
        
        return User(
            id=user_model.id,
            external_id=user_model.external_id,
            channel=Channel(user_model.channel),
            created_at=user_model.created_at
        )

    def create_attendance(self, user_id: str, channel: Channel) -> Attendance:
        att_model = AttendanceModel(
            id=new_id("att"),
            user_id=user_id,
            channel=channel.value,
        )
        self.db.add(att_model)
        self.db.commit()
        self.db.refresh(att_model)
        return Attendance(
            id=att_model.id,
            user_id=user_id,
            channel=channel,
            started_at=att_model.started_at,
            escalated=att_model.escalated
        )

    def mark_attendance_escalated(self, attendance_id: str, reason: str) -> None:
        att = self.db.query(AttendanceModel).filter(AttendanceModel.id == attendance_id).first()
        if att:
            att.escalated = True
            # For MVP, we can just save it. Handoff reasoning can be added into a separate table mapping if fully implemented.
            self.db.commit()

    def add_message(self, message: MessageRecord) -> None:
        sources_json = json.dumps([dataclasses.asdict(s) for s in message.sources])
        msg_model = MessageRecordModel(
            id=message.id,
            attendance_id=message.attendance_id,
            user_message=message.user_message,
            assistant_answer=message.assistant_answer,
            fallback=message.fallback,
            intent=message.intent.value,
            confidence=message.confidence,
            sources=sources_json,
        )
        self.db.add(msg_model)
        self.db.commit()

    def add_ai_log(self, ai_log: AiLog) -> None:
        log_model = AiLogModel(
            id=ai_log.id,
            message_id=ai_log.message_id,
            intent=ai_log.intent.value,
            relevance_score=ai_log.relevance_score,
            fallback=ai_log.fallback,
            source_document_ids=json.dumps(ai_log.source_document_ids),
            elapsed_ms=ai_log.elapsed_ms,
        )
        self.db.add(log_model)
        self.db.commit()

    def add_feedback(self, feedback: Feedback) -> None:
        fb_model = FeedbackModel(
            id=feedback.id,
            message_id=feedback.message_id,
            useful=feedback.useful,
            comment=feedback.comment
        )
        self.db.add(fb_model)
        self.db.commit()

    # The below are related to documents, mostly in-memory logic kept. We are using Qdrant directly, but for full parity we'll mock them or rely on qdrant.
    # Note: RAG chunk fetching via document is kept minimal. Let's provide a mock or simple implementation needed by assistant_service.py's _to_sources
    def get_document(self, document_id: str) -> KnowledgeDocument | None:
        # Currently the simple assistant expects this. We can load this from MySQL if we map it,
        # but the prompt requires only `title` from Qdrant metadata so we can build a mock document based on qdrant metadata directly in AssistantService.
        # Alternatively, for this iteration, return a dummy doc or we can migrate the docs to SQL.
        return KnowledgeDocument(
            id=document_id,
            title="Documento: " + document_id,
            category="general",
            channel="all",
            version="1.0",
            status="active",
            updated_at=None,
            source="",
            owner="system",
            sensitivity="internal",
            content="",
            tags=[]
        )
