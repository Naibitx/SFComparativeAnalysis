from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Enum as SqlEnum
from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.Models import Base, TimestampMixin

if TYPE_CHECKING:
    from app.Models.evaluation_run import EvaluationRun


class FindingSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class SecurityFinding(TimestampMixin, Base):
    __tablename__ = "security_findings"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    evaluation_run_id: Mapped[int] = mapped_column(
        ForeignKey("evaluation_runs.id"),
        nullable=False,
        index=True,
    )
    category: Mapped[str] = mapped_column(String(100), nullable=False)
    severity: Mapped[FindingSeverity] = mapped_column(
        SqlEnum(FindingSeverity, name="finding_severity"),
        default=FindingSeverity.MEDIUM,
        nullable=False,
    )
    title: Mapped[str] = mapped_column(String(150), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    recommendation: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    file_path: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    line_number: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    evaluation_run: Mapped["EvaluationRun"] = relationship(
        back_populates="security_findings",
    )
