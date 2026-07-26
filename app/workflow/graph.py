"""
Builds the LangGraph workflow.
"""

from langgraph.graph import StateGraph, END
from app.workflow.state import AgentCareState

from app.agents.coordinator.agent import coordinator_node
from app.agents.routing.agent import routing_node
from app.agents.appointment.agent import appointment_node


def document_node(state: AgentCareState) -> AgentCareState:
    state["current_step"] = "document"
    return state


def followup_node(state: AgentCareState) -> AgentCareState:
    state["current_step"] = "followup"
    return state


def safety_node(state: AgentCareState) -> AgentCareState:
    state["current_step"] = "safety"
    return state


def build_workflow():
    workflow = StateGraph(AgentCareState)

    workflow.add_node("coordinator", coordinator_node)
    workflow.add_node("routing", routing_node)
    workflow.add_node("appointment", appointment_node)
    workflow.add_node("document", document_node)
    workflow.add_node("followup", followup_node)
    workflow.add_node("safety", safety_node)

    workflow.set_entry_point("coordinator")
    workflow.add_edge("coordinator", "routing")
    workflow.add_edge("routing", "appointment")
    workflow.add_edge("appointment", "document")
    workflow.add_edge("document", "followup")
    workflow.add_edge("followup", "safety")
    workflow.add_edge("safety", END)

    return workflow.compile()