"""LangGraph workflow definition."""
from langgraph.graph import END, StateGraph

from src.graph.state import GraphState
from src.graph.nodes import (
    node_intake,
    node_classify_intent,
    node_retrieve_knowledge,
    node_build_context,
    node_generate_recommendation,
    node_staff_summary,
    node_escalation_check,
    node_human_review_gate,
    route_after_human_gate,
)


def build_support_graph():
    graph = StateGraph(GraphState)

    graph.add_node("intake", node_intake)
    graph.add_node("classify_intent", node_classify_intent)
    graph.add_node("retrieve_knowledge", node_retrieve_knowledge)
    graph.add_node("build_context", node_build_context)
    graph.add_node("generate_recommendation", node_generate_recommendation)
    graph.add_node("staff_summary", node_staff_summary)
    graph.add_node("escalation_check", node_escalation_check)
    graph.add_node("human_review_gate", node_human_review_gate)

    graph.set_entry_point("intake")
    graph.add_edge("intake", "classify_intent")
    graph.add_edge("classify_intent", "retrieve_knowledge")
    graph.add_edge("retrieve_knowledge", "build_context")
    graph.add_edge("build_context", "generate_recommendation")
    graph.add_edge("generate_recommendation", "staff_summary")
    graph.add_edge("staff_summary", "escalation_check")
    graph.add_edge("escalation_check", "human_review_gate")
    graph.add_conditional_edges(
        "human_review_gate",
        route_after_human_gate,
        {"save_pending": END, "save_approved": END},
    )

    return graph.compile()


_support_graph = None


def get_support_graph():
    global _support_graph
    if _support_graph is None:
        _support_graph = build_support_graph()
    return _support_graph
