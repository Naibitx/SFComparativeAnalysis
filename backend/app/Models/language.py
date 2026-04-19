from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import Enum as SqlEnum
from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.Models import Base, TimestampMixin

if TYPE_CHECKING:
    from app.Models.coding_task import CodingTask
    from app.Models.evaluation_run import EvaluationRun


class LanguageCategory(str, Enum):
    SCRIPTING = "scripting"
    COMPILED = "compiled"
    QUERY = "query"
    MARKUP = "markup"
    OTHER = "other"


class Language(TimestampMixin, Base):
    __tablename__ = "languages"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    slug: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    file_extension: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    category: Mapped[LanguageCategory] = mapped_column(
        SqlEnum(LanguageCategory, name="language_category"),
        default=LanguageCategory.SCRIPTING,
        nullable=False,
    )
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    coding_tasks: Mapped[List["CodingTask"]] = relationship(
        back_populates="default_language",
    )
    evaluation_runs: Mapped[List["EvaluationRun"]] = relationship(
        back_populates="language",
    )
