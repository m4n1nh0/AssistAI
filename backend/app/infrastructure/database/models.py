from datetime import datetime, UTC
from typing import Optional

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from app.domain.enums import Channel, Intent


class Base(DeclarativeBase):
    pass


def utc_now() -> datetime:
    return datetime.now(UTC)


class UserModel(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    external_id: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    channel: Mapped[str] = mapped_column(String(50))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)


class AttendanceModel(Base):
    __tablename__ = "attendances"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    channel: Mapped[str] = mapped_column(String(50))
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    escalated: Mapped[bool] = mapped_column(Boolean, default=False)

    user: Mapped["UserModel"] = relationship()


class MessageRecordModel(Base):
    __tablename__ = "message_records"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    attendance_id: Mapped[str] = mapped_column(ForeignKey("attendances.id"), index=True)
    user_message: Mapped[str] = mapped_column(Text)
    assistant_answer: Mapped[str] = mapped_column(Text)
    fallback: Mapped[bool] = mapped_column(Boolean, default=False)
    intent: Mapped[str] = mapped_column(String(50))
    confidence: Mapped[float] = mapped_column(Float)
    sources: Mapped[Optional[str]] = mapped_column(Text, comment="JSON string of sources")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    attendance: Mapped["AttendanceModel"] = relationship()


class FeedbackModel(Base):
    __tablename__ = "feedbacks"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    message_id: Mapped[str] = mapped_column(ForeignKey("message_records.id"), index=True, unique=True)
    useful: Mapped[bool] = mapped_column(Boolean)
    comment: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    message: Mapped["MessageRecordModel"] = relationship()


class AiLogModel(Base):
    __tablename__ = "ai_logs"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    message_id: Mapped[str] = mapped_column(ForeignKey("message_records.id"), index=True)
    intent: Mapped[str] = mapped_column(String(50))
    relevance_score: Mapped[float] = mapped_column(Float)
    fallback: Mapped[bool] = mapped_column(Boolean, default=False)
    source_document_ids: Mapped[Optional[str]] = mapped_column(Text, comment="JSON list of strings")
    elapsed_ms: Mapped[int] = mapped_column(Float)  # storing ms, can be int/float in DB depending on precision
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    message: Mapped["MessageRecordModel"] = relationship()


class HandoffModel(Base):
    __tablename__ = "handoffs"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    attendance_id: Mapped[str] = mapped_column(ForeignKey("attendances.id"), index=True)
    reason: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    attendance: Mapped["AttendanceModel"] = relationship()
