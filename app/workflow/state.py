"""
Typed state shared across all LangGraph nodes.
"""

from typing import TypedDict, List, Optional, Dict, Any
from langchain_core.messages import BaseMessage


class AgentCareState(TypedDict):
    messages: List[BaseMessage]
    patient_id: Optional[str]
    intent: Optional[str]
    current_step: Optional[str]
    agent_outputs: Dict[str, Any]
    error: Optional[str]

    # NEW
    thread_id: Optional[str]