from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, JSON, String, Text
from sqlalchemy.orm import relationship

from app.db.session import Base


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


class AttendanceModel(Base):
    __tablename__ = "attendances"

    id = Column(String(64), primary_key=True)
    user_id = Column(String(128), nullable=False)
    channel = Column(String(32), nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=now_utc)

    messages = relationship("MessageModel", back_populates="attendance", cascade="all, delete-orphan")


class MessageModel(Base):
    __tablename__ = "messages"

    id = Column(String(64), primary_key=True)
    attendance_id = Column(String(64), ForeignKey("attendances.id"), nullable=False)
    user_message = Column(Text, nullable=False)
    assistant_answer = Column(Text, nullable=False)
    fallback = Column(Boolean, nullable=False, default=False)
    intent = Column(String(64), nullable=False)
    confidence = Column(Float, nullable=False)
    sources = Column(JSON, nullable=False, default=list)
    created_at = Column(DateTime(timezone=True), nullable=False, default=now_utc)

    attendance = relationship("AttendanceModel", back_populates="messages")


class FeedbackModel(Base):
    __tablename__ = "feedbacks"

    id = Column(String(64), primary_key=True)
    message_id = Column(String(64), nullable=False)
    useful = Column(Boolean, nullable=False)
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=now_utc)
