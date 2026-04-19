from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.Models import Base, TimestampMixin

if TYPE_CHECKING:
    from app.Models.evaluation_run import EvaluationRun
    from app.Models.language import Language


class CodingTask(TimestampMixin, Base):
    __tablename__ = "coding_tasks"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    task_code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    prompt_template: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    difficulty_level: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    default_language_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("languages.id"),
        nullable=True,
    )

    default_language: Mapped[Optional["Language"]] = relationship(
        back_populates="coding_tasks",
    )
    evaluation_runs: Mapped[List["EvaluationRun"]] = relationship(
        back_populates="coding_task",
        cascade="all, delete-orphan",
    )
