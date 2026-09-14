from pydantic import BaseModel, ConfigDict, Field


class StrictModel(BaseModel):
    """Reject unexpected structured-output fields."""

    model_config = ConfigDict(extra="forbid")


class Citation(StrictModel):
    """Source evidence supporting an answer."""

    document_id: str
    document_name: str
    section: str
    chunk_id: str
    similarity_score: float


class RagAnswer(StrictModel):
    """Validated result returned by the RAG workflow."""

    answer: str = Field(min_length=1)
    abstained: bool
    citations: list[Citation]
    retrieval_top_score: float | None
    prompt_version: str
    llm_model: str | None = None
    prompt_tokens: int | None = Field(default=None, ge=0)
    completion_tokens: int | None = Field(default=None, ge=0)


class ModelAnswer(StrictModel):
    """Structured content that the LLM must generate."""

    answer: str = Field(min_length=1)
    citation_ranks: list[int] = Field(min_length=1)
