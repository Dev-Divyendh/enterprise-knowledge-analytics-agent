import json
import logging
from uuid import UUID

from enterprise_knowledge_analytics_agent.observability.logging import (
    JsonFormatter,
    get_request_id,
    normalize_request_id,
    reset_request_id,
    set_request_id,
)


def test_json_formatter_emits_safe_structured_fields() -> None:
    record = logging.LogRecord(
        name="enterprise_knowledge_analytics_agent",
        level=logging.INFO,
        pathname=__file__,
        lineno=20,
        msg="workflow_completed",
        args=(),
        exc_info=None,
    )
    record.event = "workflow_completed"
    record.request_id = "request-123"
    record.route = "policy_rag"
    record.latency_ms = 12.345
    record.prompt_tokens = 100

    payload = json.loads(JsonFormatter().format(record))

    assert payload["level"] == "INFO"
    assert payload["message"] == "workflow_completed"
    assert payload["event"] == "workflow_completed"
    assert payload["request_id"] == "request-123"
    assert payload["route"] == "policy_rag"
    assert payload["latency_ms"] == 12.345
    assert payload["prompt_tokens"] == 100
    assert "sql" not in payload
    assert "question" not in payload
    assert "rows" not in payload


def test_safe_caller_request_id_is_preserved() -> None:
    assert normalize_request_id("client-request_123") == "client-request_123"


def test_unsafe_request_id_is_replaced() -> None:
    generated = normalize_request_id("unsafe\nrequest")

    UUID(generated)
    assert generated != "unsafe\nrequest"


def test_missing_request_id_is_generated() -> None:
    generated = normalize_request_id(None)

    UUID(generated)


def test_request_id_context_is_restored() -> None:
    assert get_request_id() == "unknown"

    token = set_request_id("request-456")

    try:
        assert get_request_id() == "request-456"
    finally:
        reset_request_id(token)

    assert get_request_id() == "unknown"
