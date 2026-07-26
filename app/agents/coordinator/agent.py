"""
Coordinator agent node that analyzes patient intent and plans the workflow.
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
from app.agents.coordinator.prompt import COORDINATOR_SYSTEM_PROMPT
from app.tools.patient_lookup import patient_lookup
from app.tools.audit_tool import audit_log
from app.tools.workflow_tool import workflow_status

# Tools the coordinator may call
COORDINATOR_TOOLS = [
    patient_lookup,
    audit_log,
    workflow_status,
]


def coordinator_node(state: AgentCareState) -> AgentCareState:
    """
    LangGraph node:
    - Understands patient intent
    - Invokes tools
    - Produces a structured workflow plan
    - Stores executed tool information
    """

    state["current_step"] = "coordinator"

    # Build conversation
    messages = [
        SystemMessage(content=COORDINATOR_SYSTEM_PROMPT),
        HumanMessage(content=state.get("intent", "") or "No intent provided"),
    ]

    # Track executed tools
    executed_tools = []

    llm = get_llm()
    llm_with_tools = llm.bind_tools(COORDINATOR_TOOLS)

    try:
        ai_msg = llm_with_tools.invoke(messages)
        messages.append(ai_msg)

        # Continue until the LLM no longer requests tools
        while ai_msg.tool_calls:

            for tool_call in ai_msg.tool_calls:

                tool_name = tool_call["name"]
                tool_args = tool_call["args"]
                
                if tool_name == "patient_lookup":
                    tool_args["user_id"] = state["patient_id"]

                try:

                    if tool_name == "patient_lookup":
                        result = patient_lookup.invoke(tool_args)

                    elif tool_name == "audit_log":
                        result = audit_log.invoke(tool_args)

                    elif tool_name == "workflow_status":
                        result = workflow_status.invoke(tool_args)

                    else:
                        result = f"Unknown tool: {tool_name}"

                    # Record successful execution
                    executed_tools.append(
                        {
                            "tool": tool_name,
                            "status": "success",
                            "arguments": tool_args,
                        }
                    )

                except Exception as tool_error:

                    result = f"Tool execution failed: {tool_error}"

                    executed_tools.append(
                        {
                            "tool": tool_name,
                            "status": "failed",
                            "arguments": tool_args,
                            "error": str(tool_error),
                        }
                    )

                messages.append(
                    ToolMessage(
                        content=str(result),
                        tool_call_id=tool_call["id"],
                    )
                )

            # Ask the LLM what to do next
            ai_msg = llm_with_tools.invoke(messages)
            messages.append(ai_msg)

    except Exception as e:
        state["error"] = f"Coordinator error: {e}"
        return state

    # Parse final JSON plan
    try:

        plan_text = ai_msg.content or ""

        # Remove markdown code fences if present
        if "```" in plan_text:
            plan_text = plan_text.replace("```json", "")
            plan_text = plan_text.replace("```", "")
            plan_text = plan_text.strip()

        # Extract the first JSON object from the response
        match = re.search(r"\{.*\}", plan_text, re.DOTALL)

        if not match:
            raise ValueError(
                f"No JSON object found in LLM response.\nResponse was:\n{plan_text}"
            )

        json_text = match.group(0)

        plan = json.loads(json_text)

    except Exception as e:

        state["error"] = f"Coordinator plan parsing failed: {e}"

        plan = {
            "intent_category": "other",
            "department": "",
            "next_step": "routing",
            "plan_description": "Plan could not be parsed",
            "requires_escalation": True,
        }

    # Update workflow state
    state["intent"] = plan.get(
        "intent_category",
        state.get("intent"),
    )

    state["agent_outputs"]["coordinator"] = {
        "plan": plan,
        "tool_calls": executed_tools,
    }

    return state