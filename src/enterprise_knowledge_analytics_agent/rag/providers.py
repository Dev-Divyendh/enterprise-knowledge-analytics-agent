from collections.abc import Mapping
from dataclasses import dataclass
from time import perf_counter
from typing import Any, Protocol

import httpx
from pydantic import BaseModel, ConfigDict


@dataclass(frozen=True)
class GenerationResult:
    """Normalized result returned by any LLM provider."""

    content: str
    model: str
    prompt_tokens: int | None
    completion_tokens: int | None
    latency_ms: float


class LLMProvider(Protocol):
    """Minimum behavior required from an LLM provider."""

    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        response_format: Mapping[str, Any],
    ) -> GenerationResult:
        """Generate one structured response."""

        ...


class _OllamaMessage(BaseModel):
    model_config = ConfigDict(extra="ignore")

    content: str


class _OllamaResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")

    model: str
    message: _OllamaMessage
    prompt_eval_count: int | None = None
    eval_count: int | None = None


class OllamaProvider:
    """Call a locally running Ollama model."""

    def __init__(
        self,
        model: str = "qwen3.5:4b",
        base_url: str = "http://localhost:11434",
        timeout_seconds: float = 120.0,
        max_attempts: int = 2,
    ) -> None:
        if max_attempts < 1:
            raise ValueError("max_attempts must be at least 1")

        self._model = model
        self._base_url = base_url.rstrip("/")
        self._timeout_seconds = timeout_seconds
        self._max_attempts = max_attempts

    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        response_format: Mapping[str, Any],
    ) -> GenerationResult:
        """Request non-streaming structured output from Ollama."""

        payload: dict[str, object] = {
            "model": self._model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "stream": False,
            "think": False,
            "format": dict(response_format),
            "options": {
                "temperature": 0,
            },
        }

        started_at = perf_counter()
        last_error: httpx.TransportError | None = None

        for attempt in range(1, self._max_attempts + 1):
            try:
                response = httpx.post(
                    f"{self._base_url}/api/chat",
                    json=payload,
                    timeout=self._timeout_seconds,
                )
                response.raise_for_status()
                parsed_response = _OllamaResponse.model_validate_json(response.text)

                return GenerationResult(
                    content=parsed_response.message.content,
                    model=parsed_response.model,
                    prompt_tokens=parsed_response.prompt_eval_count,
                    completion_tokens=parsed_response.eval_count,
                    latency_ms=round(
                        (perf_counter() - started_at) * 1000,
                        3,
                    ),
                )
            except httpx.TransportError as error:
                last_error = error

                if attempt == self._max_attempts:
                    break

        raise RuntimeError(
            f"Ollama request failed after {self._max_attempts} attempts"
        ) from last_error
