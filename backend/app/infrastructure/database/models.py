from datetime import UTC, datetime

from sqlalchemy import (
    DECIMAL,
    Boolean,
    DateTime,
    Integer,
    String,
    Text,
    create_engine,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker


class Base(DeclarativeBase):
    pass


class UserModel(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    external_id: Mapped[str] = mapped_column(String(128), nullable=False)
    channel: Mapped[str] = mapped_column(String(32), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(UTC)
    )


class AttendanceModel(Base):
    __tablename__ = "attendances"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(64), nullable=False)
    channel: Mapped[str] = mapped_column(String(32), nullable=False)
    escalated: Mapped[bool] = mapped_column(Boolean, default=False)
    started_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(UTC)
    )


class MessageModel(Base):
    __tablename__ = "messages"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    attendance_id: Mapped[str] = mapped_column(String(64), nullable=False)
    user_message: Mapped[str] = mapped_column(Text, nullable=False)
    assistant_answer: Mapped[str] = mapped_column(Text, nullable=False)
    fallback: Mapped[bool] = mapped_column(Boolean, default=False)
    intent: Mapped[str] = mapped_column(String(64), nullable=True)
    confidence: Mapped[float] = mapped_column(
        DECIMAL(5, 4), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(UTC)
    )


class DocumentModel(Base):
    __tablename__ = "documents"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    category: Mapped[str] = mapped_column(String(128), nullable=False)
    channel: Mapped[str] = mapped_column(String(32), nullable=False)
    version: Mapped[str] = mapped_column(String(32), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(UTC)
    )
    source: Mapped[str] = mapped_column(String(255), nullable=True)
    owner: Mapped[str] = mapped_column(String(128), nullable=True)
    sensitivity: Mapped[str] = mapped_column(String(64), nullable=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)


class DocumentChunkModel(Base):
    __tablename__ = "document_chunks"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    document_id: Mapped[str] = mapped_column(String(64), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    chunk_index: Mapped[int] = mapped_column(Integer, default=1)
    indexed_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(UTC)
    )


class FeedbackModel(Base):
    __tablename__ = "feedbacks"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    message_id: Mapped[str] = mapped_column(String(64), nullable=False)
    useful: Mapped[bool] = mapped_column(Boolean, nullable=False)
    comment: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(UTC)
    )


class AiLogModel(Base):
    __tablename__ = "ai_logs"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    message_id: Mapped[str] = mapped_column(String(64), nullable=False)
    intent: Mapped[str] = mapped_column(String(64), nullable=True)
    relevance_score: Mapped[float] = mapped_column(
        DECIMAL(5, 4), nullable=True
    )
    fallback: Mapped[bool] = mapped_column(Boolean, default=False)
    source_document_ids: Mapped[str] = mapped_column(Text, nullable=True)
    elapsed_ms: Mapped[int] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(UTC)
    )


class HandoffModel(Base):
    __tablename__ = "handoffs"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    attendance_id: Mapped[str] = mapped_column(String(64), nullable=False)
    reason: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(UTC)
    )


class ToolCallModel(Base):
    __tablename__ = "tool_calls"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    message_id: Mapped[str] = mapped_column(String(64), nullable=False)
    tool_name: Mapped[str] = mapped_column(String(128), nullable=False)
    input_payload: Mapped[str] = mapped_column(Text, nullable=True)
    output_payload: Mapped[str] = mapped_column(Text, nullable=True)
    success: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(UTC)
    )


def create_session_maker(database_url: str):
    engine = create_engine(database_url, pool_pre_ping=True)
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)
