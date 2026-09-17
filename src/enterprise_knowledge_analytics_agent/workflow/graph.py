# pyright: reportMissingTypeStubs=false, reportUnknownMemberType=false
from time import perf_counter
from typing import Any, NotRequired, TypedDict, cast

from langgraph.graph import END, START, StateGraph
from sqlalchemy import Engine

from enterprise_knowledge_analytics_agent.analytics.service import (
    AMBIGUOUS_EXPENSE_QUESTION,
    AMBIGUOUS_QUARTER_QUESTION,
    APPROVED_ENGINEERING_QUESTION,
    DESTRUCTIVE_REFUSAL_MESSAGE,
    EXPENSE_CLARIFICATION_MESSAGE,
    GENERAL_CLARIFICATION_MESSAGE,
    QUARTER_CLARIFICATION_MESSAGE,
    RESTRICTED_DATA_REFUSAL_MESSAGE,
    answer_analytics_question,
)
from enterprise_knowledge_analytics_agent.rag.providers import LLMProvider
from enterprise_knowledge_analytics_agent.rag.service import answer_question
from enterprise_knowledge_analytics_agent.retrieval.embeddings import (
    EmbeddingProvider,
)
from enterprise_knowledge_analytics_agent.workflow.domain import (
    WorkflowAnswer,
    WorkflowRoute,
)
from enterprise_knowledge_analytics_agent.workflow.routing import (
    DESTRUCTIVE_PATTERN,
    classify_question,
)


class WorkflowState(TypedDict):
    """State passed between controlled workflow nodes."""

    question: str
    route: NotRequired[WorkflowRoute]
    result: NotRequired[WorkflowAnswer]


def build_workflow(
    *,
    llm_provider: LLMProvider,
    embedding_provider: EmbeddingProvider,
    engine: Engine,
) -> Any:
    """Build and compile the controlled enterprise workflow."""

    def route_node(state: WorkflowState) -> dict[str, WorkflowRoute]:
        question = state["question"]

        return {
            "route": classify_question(question),
        }

    def select_route(state: WorkflowState) -> WorkflowRoute:
        route = state.get("route")

        if route is None:
            raise RuntimeError("workflow route was not assigned")

        return route

    def policy_rag_node(
        state: WorkflowState,
    ) -> dict[str, WorkflowAnswer]:
        rag_answer = answer_question(
            question=state["question"],
            llm_provider=llm_provider,
            embedding_provider=embedding_provider,
            engine=engine,
        )

        return {
            "result": WorkflowAnswer(
                route="policy_rag",
                answer=rag_answer.answer,
                abstained=rag_answer.abstained,
                citations=rag_answer.citations,
                retrieval_top_score=rag_answer.retrieval_top_score,
                llm_model=rag_answer.llm_model,
                prompt_tokens=rag_answer.prompt_tokens,
                completion_tokens=rag_answer.completion_tokens,
            )
        }

    def text_to_sql_node(
        state: WorkflowState,
    ) -> dict[str, WorkflowAnswer]:
        analytics_answer = answer_analytics_question(
            APPROVED_ENGINEERING_QUESTION,
            llm_provider=llm_provider,
            engine=engine,
        )

        return {
            "result": WorkflowAnswer(
                route="text_to_sql",
                answer=analytics_answer.answer,
                sql=analytics_answer.sql,
                rows=analytics_answer.rows,
                llm_model=analytics_answer.llm_model,
                prompt_tokens=analytics_answer.prompt_tokens,
                completion_tokens=analytics_answer.completion_tokens,
            )
        }

    def clarification_node(
        state: WorkflowState,
    ) -> dict[str, WorkflowAnswer]:
        question = state["question"]

        if question == AMBIGUOUS_QUARTER_QUESTION:
            message = QUARTER_CLARIFICATION_MESSAGE
        elif question == AMBIGUOUS_EXPENSE_QUESTION:
            message = EXPENSE_CLARIFICATION_MESSAGE
        else:
            message = GENERAL_CLARIFICATION_MESSAGE

        return {
            "result": WorkflowAnswer(
                route="clarification",
                answer=message,
            )
        }

    def refusal_node(
        state: WorkflowState,
    ) -> dict[str, WorkflowAnswer]:
        question = state["question"]

        if DESTRUCTIVE_PATTERN.search(question) is not None:
            message = DESTRUCTIVE_REFUSAL_MESSAGE
        else:
            message = RESTRICTED_DATA_REFUSAL_MESSAGE

        return {
            "result": WorkflowAnswer(
                route="refusal",
                answer=message,
            )
        }

    workflow = StateGraph(WorkflowState)

    workflow.add_node("route", route_node)
    workflow.add_node("policy_rag", policy_rag_node)
    workflow.add_node("text_to_sql", text_to_sql_node)
    workflow.add_node("clarification", clarification_node)
    workflow.add_node("refusal", refusal_node)

    workflow.add_edge(START, "route")
    workflow.add_conditional_edges(
        "route",
        select_route,
        {
            "policy_rag": "policy_rag",
            "text_to_sql": "text_to_sql",
            "clarification": "clarification",
            "refusal": "refusal",
        },
    )

    workflow.add_edge("policy_rag", END)
    workflow.add_edge("text_to_sql", END)
    workflow.add_edge("clarification", END)
    workflow.add_edge("refusal", END)

    return workflow.compile()


def run_workflow(
    question: str,
    *,
    llm_provider: LLMProvider,
    embedding_provider: EmbeddingProvider,
    engine: Engine,
) -> WorkflowAnswer:
    """Execute one question through the compiled controlled workflow."""

    normalized_question = question.strip()

    if not normalized_question:
        raise ValueError("question must not be empty")

    started_at = perf_counter()
    workflow = build_workflow(
        llm_provider=llm_provider,
        embedding_provider=embedding_provider,
        engine=engine,
    )

    final_state = cast(
        WorkflowState,
        workflow.invoke(
            {
                "question": normalized_question,
            }
        ),
    )
    result = final_state.get("result")

    if result is None:
        raise RuntimeError("workflow completed without a result")

    return result.model_copy(
        update={
            "total_latency_ms": round(
                (perf_counter() - started_at) * 1000,
                3,
            )
        }
    )
