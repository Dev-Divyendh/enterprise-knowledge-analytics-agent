import json
import logging
import re
from contextvars import ContextVar, Token
from datetime import UTC, datetime
from uuid import uuid4

REQUEST_ID_HEADER = "X-Request-ID"
REQUEST_ID_PATTERN = re.compile(r"^[A-Za-z0-9._-]{1,128}$")

_request_id_context: ContextVar[str] = ContextVar(
    "request_id",
    default="unknown",
)

SAFE_LOG_FIELDS = (
    "event",
    "request_id",
    "method",
    "path",
    "status_code",
    "latency_ms",
    "route",
    "outcome",
    "abstained",
    "llm_model",
    "prompt_tokens",
    "completion_tokens",
    "retrieval_top_score",
)


class JsonFormatter(logging.Formatter):
    """Serialize application log records as one-line JSON."""

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, object] = {
            "timestamp": datetime.now(UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        for field_name in SAFE_LOG_FIELDS:
            field_value = getattr(record, field_name, None)

            if field_value is not None:
                payload[field_name] = field_value

        if record.exc_info is not None:
            payload["exception"] = self.formatException(record.exc_info)

        return json.dumps(
            payload,
            ensure_ascii=False,
            separators=(",", ":"),
            default=str,
        )


def normalize_request_id(candidate: str | None) -> str:
    """Accept a safe caller ID or generate a new opaque request ID."""

    if candidate is not None and REQUEST_ID_PATTERN.fullmatch(candidate):
        return candidate

    return str(uuid4())


def set_request_id(request_id: str) -> Token[str]:
    """Bind a request ID to the current async execution context."""

    return _request_id_context.set(request_id)


def reset_request_id(token: Token[str]) -> None:
    """Restore the previous request context."""

    _request_id_context.reset(token)


def get_request_id() -> str:
    """Return the request ID bound to the current execution context."""

    return _request_id_context.get()


def configure_logging(log_level: str) -> logging.Logger:
    """Configure the application logger with deterministic JSON output."""

    logger = logging.getLogger("enterprise_knowledge_analytics_agent")
    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())

    logger.handlers.clear()
    logger.addHandler(handler)
    logger.setLevel(log_level)
    logger.propagate = False

    return logger


def get_application_logger() -> logging.Logger:
    """Return the configured application logger."""

    return logging.getLogger("enterprise_knowledge_analytics_agent")
