import pytest

from enterprise_knowledge_analytics_agent import main


def test_main_prints_project_name(capsys: pytest.CaptureFixture[str]) -> None:
    main()

    captured = capsys.readouterr()

    assert captured.out == "Hello from enterprise-knowledge-analytics-agent!\n"
    assert captured.err == ""
