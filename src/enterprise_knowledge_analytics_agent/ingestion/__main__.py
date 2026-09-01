import argparse
import json
from pathlib import Path
from typing import Any

from enterprise_knowledge_analytics_agent.ingestion.service import ingest_markdown


def _result_to_json(result: object) -> str:
    values: dict[str, Any] = vars(result)
    serializable = {
        key: str(value) if key.endswith("_id") else value for key, value in values.items()
    }
    return json.dumps(serializable, indent=2, sort_keys=True)


def main() -> None:
    """Run local Markdown ingestion from the command line."""

    parser = argparse.ArgumentParser(description="Ingest one Markdown document")
    parser.add_argument("path", type=Path)
    arguments = parser.parse_args()

    result = ingest_markdown(arguments.path)
    print(_result_to_json(result))


if __name__ == "__main__":
    main()
