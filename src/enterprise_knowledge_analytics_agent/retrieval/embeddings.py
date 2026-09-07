from collections.abc import Sequence
from typing import Protocol, cast

from sentence_transformers import SentenceTransformer

DEFAULT_EMBEDDING_MODEL = "BAAI/bge-small-en-v1.5"
DEFAULT_EMBEDDING_MODEL_VERSION = "v1.5"
BGE_QUERY_INSTRUCTION = "Represent this sentence for searching relevant passages: "


class EmbeddingProvider(Protocol):
    """Behavior required from an embedding implementation."""

    @property
    def model_name(self) -> str:
        """Return the stored model identifier."""

        ...

    @property
    def model_version(self) -> str:
        """Return the stored model version."""

        ...

    @property
    def dimension(self) -> int:
        """Return the vector dimension."""

        ...

    def embed_documents(self, texts: Sequence[str]) -> list[list[float]]:
        """Embed document passages."""

        ...

    def embed_query(self, question: str) -> list[float]:
        """Embed one retrieval question."""

        ...


class _MatrixWithToList(Protocol):
    """Typed view of an embedding matrix."""

    def tolist(self) -> list[list[float]]:
        """Convert the matrix into nested Python lists."""

        ...


class _SentenceEncoder(Protocol):
    """Narrow typed view of the library method that we use."""

    def encode(
        self,
        sentences: list[str],
        *,
        batch_size: int,
        normalize_embeddings: bool,
        show_progress_bar: bool,
        convert_to_numpy: bool,
    ) -> object:
        """Encode text using the required options."""

        ...


class SentenceTransformerEmbeddingProvider:
    """Generate normalized BGE embeddings using Sentence Transformers."""

    def __init__(
        self,
        model_name: str = DEFAULT_EMBEDDING_MODEL,
        model_version: str = DEFAULT_EMBEDDING_MODEL_VERSION,
        device: str = "cpu",
        batch_size: int = 32,
    ) -> None:
        self._model_name = model_name
        self._model_version = model_version
        self._batch_size = batch_size
        self._model = SentenceTransformer(model_name, device=device)

        dimension = self._model.get_embedding_dimension()

        if dimension is None:
            raise RuntimeError("embedding model did not report its dimension")

        self._dimension = dimension

    @property
    def model_name(self) -> str:
        return self._model_name

    @property
    def model_version(self) -> str:
        return self._model_version

    @property
    def dimension(self) -> int:
        return self._dimension

    def embed_documents(
        self,
        texts: Sequence[str],
    ) -> list[list[float]]:
        """Embed document text without a query instruction."""

        if not texts:
            return []

        return self._encode(list(texts))

    def embed_query(self, question: str) -> list[float]:
        """Embed a question using BGE's retrieval instruction."""

        normalized_question = question.strip()

        if not normalized_question:
            raise ValueError("question must not be empty")

        vectors = self._encode([f"{BGE_QUERY_INSTRUCTION}{normalized_question}"])
        return vectors[0]

    def _encode(self, texts: list[str]) -> list[list[float]]:
        encoder = cast(_SentenceEncoder, self._model)
        encoded = encoder.encode(
            texts,
            batch_size=self._batch_size,
            normalize_embeddings=True,
            show_progress_bar=False,
            convert_to_numpy=True,
        )
        matrix = cast(_MatrixWithToList, encoded)

        return [[float(value) for value in vector] for vector in matrix.tolist()]
