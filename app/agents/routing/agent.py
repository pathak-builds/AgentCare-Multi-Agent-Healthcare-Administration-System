"""
Department Routing Agent node.
"""
import json
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, ToolMessage
from app.workflow.state import AgentCareState
from app.llm import get_llm
from app.agents.routing.prompt import ROUTING_SYSTEM_PROMPT
from app.tools.department_lookup import department_list

ROUTING_TOOLS = [department_list]

def routing_node(state: AgentCareState) -> AgentCareState:
    """
    LangGraph node: maps patient intent to a department using real DB data.
    """
    state["current_step"] = "routing"

    # Prepare context from previous steps
    coordinator_plan = state.get("agent_outputs", {}).get("coordinator", {}).get("plan", {})
    intent = state.get("intent", "")
    original_messages = state.get("messages", [])
    # Use the last human message as the user request (or intent string)
    user_request = intent
    if original_messages:
        for msg in reversed(original_messages):
            if hasattr(msg, "content") and isinstance(msg, HumanMessage):
                user_request = msg.content
                break

    # Build prompt
    system_msg = SystemMessage(content=ROUTING_SYSTEM_PROMPT)
    human_msg = HumanMessage(content=(
        f"Coordinator plan: {json.dumps(coordinator_plan)}\n"
        f"Original request: {user_request}"
    ))

    messages = [system_msg, human_msg]

    llm = get_llm()
    llm_with_tools = llm.bind_tools(ROUTING_TOOLS)

    # Tool calling loop
    try:
        ai_msg = llm_with_tools.invoke(messages)
        messages.append(ai_msg)

        while ai_msg.tool_calls:
            for tool_call in ai_msg.tool_calls:
                if tool_call["name"] == "department_list":
                    result = department_list.invoke({})
                else:
                    result = "Unknown tool"
                messages.append(ToolMessage(content=str(result), tool_call_id=tool_call["id"]))
            ai_msg = llm_with_tools.invoke(messages)
            messages.append(ai_msg)
    except Exception as e:
        state["error"] = f"Routing error: {str(e)}"
        return state

    # Parse final AI message as JSON
    try:
        content = ai_msg.content
        # Strip markdown if present
        if "```" in content:
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
        routing_result = json.loads(content)
    except Exception as e:
        state["error"] = f"Routing output parsing failed: {e}"
        routing_result = {
            "department_id": None,
            "department_name": None,
            "confidence": 0.0,
            "escalation_reason": "Failed to parse routing output",
        }

    # Store in state
    state["agent_outputs"]["routing"] = routing_result

    # If escalation reason present, we might want to set a flag for later
    # but the Safety agent can read this output.
    return state