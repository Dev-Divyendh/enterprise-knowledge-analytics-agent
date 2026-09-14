from functools import lru_cache

from sqlalchemy import Engine

from enterprise_knowledge_analytics_agent.persistence.database import (
    create_database_engine,
)
from enterprise_knowledge_analytics_agent.rag.providers import (
    LLMProvider,
    OllamaProvider,
)
from enterprise_knowledge_analytics_agent.retrieval.embeddings import (
    EmbeddingProvider,
    SentenceTransformerEmbeddingProvider,
)


@lru_cache
def get_database_engine() -> Engine:
    """Create and reuse the application's database connection pool."""

    return create_database_engine()


@lru_cache
def get_embedding_provider() -> EmbeddingProvider:
    """Load and reuse the local embedding model."""

    return SentenceTransformerEmbeddingProvider()


@lru_cache
def get_llm_provider() -> LLMProvider:
    """Create and reuse the local Ollama client."""

    return OllamaProvider()
