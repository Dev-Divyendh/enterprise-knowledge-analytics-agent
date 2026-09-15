import argparse
from pathlib import Path

from enterprise_knowledge_analytics_agent.evaluation.golden import (
    load_golden_dataset,
)
from enterprise_knowledge_analytics_agent.evaluation.retrieval import (
    evaluate_retrieval,
)
from enterprise_knowledge_analytics_agent.persistence.database import (
    create_database_engine,
)
from enterprise_knowledge_analytics_agent.retrieval.dense import (
    RetrievedChunk,
    retrieve_dense,
)
from enterprise_knowledge_analytics_agent.retrieval.embeddings import (
    SentenceTransformerEmbeddingProvider,
)


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Evaluate exact dense retrieval against a frozen dataset."
    )
    parser.add_argument(
        "dataset",
        type=Path,
        help="Path to the frozen golden dataset.",
    )
    parser.add_argument(
        "--top-k",
        type=int,
        default=5,
        help="Number of chunks retrieved for each case.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        required=True,
        help="Path where the JSON report will be written.",
    )

    return parser.parse_args()


def main() -> None:
    arguments = parse_arguments()
    dataset = load_golden_dataset(arguments.dataset)

    engine = create_database_engine()
    embedding_provider = SentenceTransformerEmbeddingProvider()

    def retrieve(question: str, top_k: int) -> list[RetrievedChunk]:
        return retrieve_dense(
            question,
            top_k=top_k,
            provider=embedding_provider,
            engine=engine,
        )

    try:
        report = evaluate_retrieval(
            dataset,
            retrieve,
            retrieval_system="exact_dense_cosine_bge_small_v1.5",
            top_k=arguments.top_k,
        )
    finally:
        engine.dispose()

    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(
        report.model_dump_json(indent=2),
        encoding="utf-8",
    )

    print(report.metrics.model_dump_json(indent=2))
    print(f"report: {arguments.output}")


if __name__ == "__main__":
    main()
