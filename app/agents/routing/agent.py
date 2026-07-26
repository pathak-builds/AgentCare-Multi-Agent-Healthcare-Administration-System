"""
Department Routing Agent node.
"""

import json
import re

from langchain_core.messages import (
    SystemMessage,
    HumanMessage,
    ToolMessage,
)

from app.workflow.state import AgentCareState
from app.llm import get_llm
from app.agents.routing.prompt import ROUTING_SYSTEM_PROMPT
from app.tools.department_lookup import department_list


ROUTING_TOOLS = [
    department_list,
]


def routing_node(state: AgentCareState) -> AgentCareState:
    """
    LangGraph node:
    Maps appointment-related administrative requests
    to the correct hospital department.
    """

    state["current_step"] = "routing"

    # ---------------------------------------------------------
    # Read coordinator output
    # ---------------------------------------------------------

    coordinator_plan = (
        state.get("agent_outputs", {})
        .get("coordinator", {})
        .get("plan", {})
    )

    intent_category = coordinator_plan.get("intent_category")

    # ---------------------------------------------------------
    # Skip routing when a department is not required
    # ---------------------------------------------------------

    NON_ROUTING_INTENTS = {
        "upload_document",
        "check_status",
    }

    if intent_category in NON_ROUTING_INTENTS:

        state["agent_outputs"]["routing"] = {
            "department_id": None,
            "department_name": "",
            "confidence": 1.0,
            "escalation_reason": None,
        }

        return state

    # ---------------------------------------------------------
    # Recover original user request
    # ---------------------------------------------------------

    intent = state.get("intent", "")
    original_messages = state.get("messages", [])

    user_request = intent

    for msg in reversed(original_messages):
        if isinstance(msg, HumanMessage):
            user_request = msg.content
            break

    # ---------------------------------------------------------
    # Build prompt
    # ---------------------------------------------------------

    messages = [
        SystemMessage(content=ROUTING_SYSTEM_PROMPT),
        HumanMessage(
            content=(
                f"Coordinator plan:\n"
                f"{json.dumps(coordinator_plan, indent=2)}\n\n"
                f"Original request:\n"
                f"{user_request}"
            )
        ),
    ]

    llm = get_llm()
    llm_with_tools = llm.bind_tools(ROUTING_TOOLS)

    # ---------------------------------------------------------
    # Tool calling loop
    # ---------------------------------------------------------

    try:

        ai_msg = llm_with_tools.invoke(messages)
        messages.append(ai_msg)

        while ai_msg.tool_calls:

            for tool_call in ai_msg.tool_calls:

                tool_name = tool_call["name"]

                if tool_name == "department_list":
                    result = department_list.invoke({})
                else:
                    result = "Unknown tool."

                messages.append(
                    ToolMessage(
                        content=str(result),
                        tool_call_id=tool_call["id"],
                    )
                )

            ai_msg = llm_with_tools.invoke(messages)
            messages.append(ai_msg)

    except Exception as e:

        state["error"] = f"Routing error: {e}"

        state["agent_outputs"]["routing"] = {
            "department_id": None,
            "department_name": "",
            "confidence": 0.0,
            "escalation_reason": str(e),
        }

        return state

    # ---------------------------------------------------------
    # Parse JSON returned by the LLM
    # ---------------------------------------------------------

    try:

        content = ai_msg.content or ""

        if "```" in content:
            content = content.replace("```json", "")
            content = content.replace("```", "")
            content = content.strip()

        match = re.search(r"\{.*\}", content, re.DOTALL)

        if not match:
            raise ValueError(
                f"No JSON object found.\nLLM response:\n{content}"
            )

        routing_result = json.loads(match.group())

    except Exception as e:

        state["error"] = f"Routing output parsing failed: {e}"

        routing_result = {
            "department_id": None,
            "department_name": "",
            "confidence": 0.0,
            "escalation_reason": "Failed to parse routing output.",
        }

    # ---------------------------------------------------------
    # Store routing decision
    # ---------------------------------------------------------

    state["agent_outputs"]["routing"] = routing_result

    return state