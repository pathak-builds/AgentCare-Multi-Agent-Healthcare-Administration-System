"""
Typed state shared across all LangGraph nodes.
"""
from typing import TypedDict, List, Optional, Dict, Any
from langchain_core.messages import BaseMessage

class AgentCareState(TypedDict):
    messages: List[BaseMessage]          # Full conversation history
    patient_id: Optional[str]            # Patient profile id
    intent: Optional[str]                # Administrative intent (e.g., "book_appointment")
    current_step: Optional[str]          # Current agent node name
    agent_outputs: Dict[str, Any]        # Keyed by agent name, stores structured outputs
    error: Optional[str]                 # First error encountered