"""ORM model for persisted diagnosis sessions."""

from typing import Optional

from sqlalchemy import DateTime, Float, Integer, JSON, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from database.db import Base


class SessionRecord(Base):
    __tablename__ = "sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    created_at: Mapped[Optional[object]] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    session_type: Mapped[str] = mapped_column(String(20))  # skin | leaf | joint | tf
    dataset: Mapped[Optional[str]] = mapped_column(String(80), nullable=True)
    predicted_class: Mapped[Optional[str]] = mapped_column(String(160), nullable=True)
    confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    status: Mapped[Optional[str]] = mapped_column(String(40), nullable=True)
    top_predictions: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    recommendations: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    llm_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    image: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # base64 data URL
    meta: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
