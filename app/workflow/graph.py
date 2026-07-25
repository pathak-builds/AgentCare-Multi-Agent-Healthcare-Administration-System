"""
Builds the LangGraph workflow with placeholder nodes for each agent.
"""
from langgraph.graph import StateGraph, END
from app.workflow.state import AgentCareState
from app.workflow.memory import WorkflowCheckpointer

def coordinator_node(state: AgentCareState) -> AgentCareState:
    state["current_step"] = "coordinator"
    # Placeholder: will be implemented in Phase 6
    return state

def routing_node(state: AgentCareState) -> AgentCareState:
    state["current_step"] = "routing"
    return state

def appointment_node(state: AgentCareState) -> AgentCareState:
    state["current_step"] = "appointment"
    return state

def document_node(state: AgentCareState) -> AgentCareState:
    state["current_step"] = "document"
    return state

def followup_node(state: AgentCareState) -> AgentCareState:
    state["current_step"] = "followup"
    return state

def safety_node(state: AgentCareState) -> AgentCareState:
    state["current_step"] = "safety"
    return state

def build_workflow() -> StateGraph:
    """Create and compile the multi‑agent workflow graph."""
    workflow = StateGraph(AgentCareState)

    # Add nodes
    workflow.add_node("coordinator", coordinator_node)
    workflow.add_node("routing", routing_node)
    workflow.add_node("appointment", appointment_node)
    workflow.add_node("document", document_node)
    workflow.add_node("followup", followup_node)
    workflow.add_node("safety", safety_node)

    # Define linear edges
    workflow.set_entry_point("coordinator")
    workflow.add_edge("coordinator", "routing")
    workflow.add_edge("routing", "appointment")
    workflow.add_edge("appointment", "document")
    workflow.add_edge("document", "followup")
    workflow.add_edge("followup", "safety")
    workflow.add_edge("safety", END)

    # Compile with our custom SQLite checkpointer
    # checkpointer = WorkflowCheckpointer()
    # return workflow.compile(checkpointer=checkpointer)
    
    return workflow.compile()