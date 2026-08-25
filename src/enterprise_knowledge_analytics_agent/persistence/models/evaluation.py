import enum
import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, Enum, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from enterprise_knowledge_analytics_agent.persistence.models.base import Base


def enum_values(enum_class: type[enum.Enum]) -> list[str]:
    """Return the database values defined by a Python enum."""

    return [str(item.value) for item in enum_class]


class EvaluationRunType(enum.StrEnum):
    """The part of the system being evaluated."""

    INGESTION = "ingestion"
    RETRIEVAL = "retrieval"
    RAG = "rag"
    TEXT_TO_SQL = "text_to_sql"
    ROUTING = "routing"
    END_TO_END = "end_to_end"


class EvaluationRunStatus(enum.StrEnum):
    """Current outcome of an evaluation run."""

    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class EvaluationRun(Base):
    """Configuration and results for one evaluation experiment."""

    __tablename__ = "evaluation_runs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    run_type: Mapped[EvaluationRunType] = mapped_column(
        Enum(
            EvaluationRunType,
            name="evaluation_run_type",
            values_callable=enum_values,
            native_enum=False,
            create_constraint=True,
        ),
        nullable=False,
    )
    status: Mapped[EvaluationRunStatus] = mapped_column(
        Enum(
            EvaluationRunStatus,
            name="evaluation_run_status",
            values_callable=enum_values,
            native_enum=False,
            create_constraint=True,
        ),
        nullable=False,
        default=EvaluationRunStatus.RUNNING,
    )
    dataset_version: Mapped[str] = mapped_column(String(50), nullable=False)
    configuration: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
        server_default="{}",
    )
    metrics: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
        server_default="{}",
    )
    mlflow_run_id: Mapped[str | None] = mapped_column(String(255))
    artifact_uri: Mapped[str | None] = mapped_column(Text)
    error_message: Mapped[str | None] = mapped_column(Text)
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
