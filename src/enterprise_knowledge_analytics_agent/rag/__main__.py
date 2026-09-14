import argparse

from enterprise_knowledge_analytics_agent.rag.providers import OllamaProvider
from enterprise_knowledge_analytics_agent.rag.service import answer_question


def main() -> None:
    """Ask one grounded policy question from the terminal."""

    parser = argparse.ArgumentParser(description="Ask a grounded policy question")
    parser.add_argument("question")
    arguments = parser.parse_args()

    answer = answer_question(
        question=arguments.question,
        llm_provider=OllamaProvider(),
    )
    print(answer.model_dump_json(indent=2))


if __name__ == "__main__":
    main()
