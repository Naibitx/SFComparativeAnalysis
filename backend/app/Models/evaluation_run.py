from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import Boolean, DateTime, Enum as SqlEnum
from sqlalchemy import Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.Models import Base, TimestampMixin

if TYPE_CHECKING:
    from app.Models.assistant import Assistant
    from app.Models.coding_task import CodingTask
    from app.Models.language import Language
    from app.Models.security_finding import SecurityFinding


class RunStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class EvaluationRun(TimestampMixin, Base):
    __tablename__ = "evaluation_runs"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    run_id: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    assistant_id: Mapped[int] = mapped_column(ForeignKey("assistants.id"), nullable=False)
    coding_task_id: Mapped[int] = mapped_column(ForeignKey("coding_tasks.id"), nullable=False)
    language_id: Mapped[Optional[int]] = mapped_column(ForeignKey("languages.id"), nullable=True)
    status: Mapped[RunStatus] = mapped_column(
        SqlEnum(RunStatus, name="run_status"),
        default=RunStatus.PENDING,
        nullable=False,
    )
    workspace_path: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    prompt_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    generated_code_path: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    generated_code: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    execution_output: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    execution_error: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    execution_success: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    tokens_used: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    latency_ms: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    execution_time_ms: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    overall_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    assistant: Mapped["Assistant"] = relationship(back_populates="evaluation_runs")
    coding_task: Mapped["CodingTask"] = relationship(back_populates="evaluation_runs")
    language: Mapped[Optional["Language"]] = relationship(back_populates="evaluation_runs")
    security_findings: Mapped[List["SecurityFinding"]] = relationship(
        back_populates="evaluation_run",
        cascade="all, delete-orphan",
    )
