from typing import Annotated

from fastapi import Depends, FastAPI
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import Engine

from enterprise_knowledge_analytics_agent.api.dependencies import (
    get_database_engine,
    get_embedding_provider,
    get_llm_provider,
)
from enterprise_knowledge_analytics_agent.persistence.database import (
    check_database_health,
)
from enterprise_knowledge_analytics_agent.rag.domain import RagAnswer
from enterprise_knowledge_analytics_agent.rag.providers import LLMProvider
from enterprise_knowledge_analytics_agent.rag.service import answer_question
from enterprise_knowledge_analytics_agent.retrieval.embeddings import (
    EmbeddingProvider,
)


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

app = FastAPI(
    title="Enterprise Knowledge and Analytics Agent",
    version="0.1.0",
    description=("Grounded enterprise policy question answering and safe analytics."),
)


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    """Report whether the API process is running."""

    return HealthResponse(status="healthy")


@app.get("/ready", response_model=ReadinessResponse)
def readiness(engine: DatabaseEngine) -> ReadinessResponse:
    """Report whether the API can connect to PostgreSQL."""

    database_name = check_database_health(engine)

    return ReadinessResponse(
        status="ready",
        database=database_name,
    )


@app.post("/api/v1/questions", response_model=RagAnswer)
def ask_question(
    request: QuestionRequest,
    engine: DatabaseEngine,
    embedding_provider: EmbeddingDependency,
    llm_provider: LLMDependency,
) -> RagAnswer:
    """Answer a policy question using the grounded RAG workflow."""

    return answer_question(
        question=request.question,
        llm_provider=llm_provider,
        embedding_provider=embedding_provider,
        engine=engine,
    )
