import argparse
import json
from dataclasses import asdict

from enterprise_knowledge_analytics_agent.retrieval.dense import (
    embed_document_chunks,
    retrieve_dense,
)


def main() -> None:
    """Embed document chunks or execute dense retrieval."""

    parser = argparse.ArgumentParser(description="Dense retrieval commands")
    subparsers = parser.add_subparsers(dest="command", required=True)

    embed_parser = subparsers.add_parser(
        "embed",
        help="Generate missing embeddings for a document",
    )
    embed_parser.add_argument("external_id")

    search_parser = subparsers.add_parser(
        "search",
        help="Search stored chunks",
    )
    search_parser.add_argument("question")
    search_parser.add_argument("--top-k", type=int, default=3)

    arguments = parser.parse_args()

    if arguments.command == "embed":
        result = embed_document_chunks(arguments.external_id)
        print(json.dumps(asdict(result), indent=2, sort_keys=True))
        return

    results = retrieve_dense(
        question=arguments.question,
        top_k=arguments.top_k,
    )
    print(
        json.dumps(
            [asdict(result) for result in results],
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
