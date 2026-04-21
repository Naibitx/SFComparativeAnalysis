from datetime import datetime

from sqlalchemy import DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Shared SQLAlchemy declarative base for all ORM models."""


class TimestampMixin:
    """Adds automatic created/updated timestamps to a model."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


from .assistant import Assistant  # noqa: E402,F401
from .coding_task import CodingTask  # noqa: E402,F401
from .evaluation_run import EvaluationRun  # noqa: E402,F401
from .language import Language  # noqa: E402,F401
from .security_finding import SecurityFinding  # noqa: E402,F401


__all__ = [
    "Assistant",
    "Base",
    "CodingTask",
    "EvaluationRun",
    "Language",
    "SecurityFinding",
    "TimestampMixin",
]
