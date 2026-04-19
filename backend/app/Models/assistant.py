from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import Boolean, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.Models import Base, TimestampMixin

if TYPE_CHECKING:
    from app.Models.evaluation_run import EvaluationRun


class Assistant(TimestampMixin, Base):
    __tablename__ = "assistants"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    provider: Mapped[str] = mapped_column(String(100), nullable=False)
    model_version: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    api_base_url: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    evaluation_runs: Mapped[List["EvaluationRun"]] = relationship(
        back_populates="assistant",
        cascade="all, delete-orphan",
    )
