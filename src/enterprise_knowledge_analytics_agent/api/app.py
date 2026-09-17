from collections.abc import Awaitable, Callable
from time import perf_counter
from typing import Annotated

from fastapi import Depends, FastAPI, Request, Response
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import Engine

from enterprise_knowledge_analytics_agent.api.dependencies import (
    get_database_engine,
    get_embedding_provider,
    get_llm_provider,
)
from enterprise_knowledge_analytics_agent.config import get_settings
from enterprise_knowledge_analytics_agent.observability.logging import (
    REQUEST_ID_HEADER,
    configure_logging,
    get_request_id,
    normalize_request_id,
    reset_request_id,
    set_request_id,
)
from enterprise_knowledge_analytics_agent.persistence.database import (
    check_database_health,
)
from enterprise_knowledge_analytics_agent.rag.providers import LLMProvider
from enterprise_knowledge_analytics_agent.retrieval.embeddings import (
    EmbeddingProvider,
)
from enterprise_knowledge_analytics_agent.workflow.domain import WorkflowAnswer
from enterprise_knowledge_analytics_agent.workflow.graph import run_workflow


class QuestionRequest(BaseModel):
    """Validated request accepted by the question endpoint."""

    model_config = ConfigDict(extra="forbid")

    question: str = Field(min_length=1, max_length=2_000)


class HealthResponse(BaseModel):
    """Basic process-health response."""

    status: str


class ReadinessResponse(BaseModel):
    """Response confirming that PostgreSQL is reachable."""

    status: str
    database: str


DatabaseEngine = Annotated[Engine, Depends(get_database_engine)]
EmbeddingDependency = Annotated[
    EmbeddingProvider,
    Depends(get_embedding_provider),
]
LLMDependency = Annotated[LLMProvider, Depends(get_llm_provider)]
CallNext = Callable[[Request], Awaitable[Response]]

settings = get_settings()
logger = configure_logging(settings.log_level)

app = FastAPI(
    title="Enterprise Knowledge and Analytics Agent",
    version="0.1.0",
    description=("Grounded enterprise policy question answering and safe analytics."),
)


@app.middleware("http")
async def request_context_middleware(
    request: Request,
    call_next: CallNext,
) -> Response:
    """Attach a safe request ID and emit request-level metadata."""

    request_id = normalize_request_id(request.headers.get(REQUEST_ID_HEADER))
    context_token = set_request_id(request_id)
    started_at = perf_counter()
    status_code = 500

    try:
        response = await call_next(request)
        status_code = response.status_code
        response.headers[REQUEST_ID_HEADER] = request_id

        return response
    except Exception:
        logger.exception(
            "request_failed",
            extra={
                "event": "request_failed",
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "status_code": status_code,
            },
        )
        raise
    finally:
        logger.info(
            "request_completed",
            extra={
                "event": "request_completed",
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "status_code": status_code,
                "latency_ms": round(
                    (perf_counter() - started_at) * 1000,
                    3,
                ),
            },
        )
        reset_request_id(context_token)


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    """Report whether the API process is running."""

    return HealthResponse(status="healthy")


@app.get("/ready", response_model=ReadinessResponse)
def readiness(engine: DatabaseEngine) -> ReadinessResponse:
    """Report whether PostgreSQL is reachable."""

    database_name = check_database_health(engine)

    return ReadinessResponse(
        status="ready",
        database=database_name,
    )


@app.post("/api/v1/questions", response_model=WorkflowAnswer)
def ask_question(
    request: QuestionRequest,
    engine: DatabaseEngine,
    embedding_provider: EmbeddingDependency,
    llm_provider: LLMDependency,
) -> WorkflowAnswer:
    """Route one request through the controlled enterprise workflow."""

    result = run_workflow(
        question=request.question,
        llm_provider=llm_provider,
        embedding_provider=embedding_provider,
        engine=engine,
    )
    outcome = "abstained" if result.abstained else "completed"

    logger.info(
        "workflow_completed",
        extra={
            "event": "workflow_completed",
            "request_id": get_request_id(),
            "route": result.route,
            "outcome": outcome,
            "abstained": result.abstained,
            "llm_model": result.llm_model,
            "prompt_tokens": result.prompt_tokens,
            "completion_tokens": result.completion_tokens,
            "retrieval_top_score": result.retrieval_top_score,
            "latency_ms": result.total_latency_ms,
        },
    )

    return result
