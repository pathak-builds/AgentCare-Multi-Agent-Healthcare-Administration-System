"""
Safety Agent node: reviews the entire workflow, blocks medical advice,
creates escalations when necessary, and performs the final workflow safety check.
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
from app.agents.safety.prompt import SAFETY_SYSTEM_PROMPT
from app.tools.safety_tools import (
    create_escalation,
    log_safety_audit,
)

SAFETY_TOOLS = [
    create_escalation,
    log_safety_audit,
]


def safety_node(state: AgentCareState) -> AgentCareState:
    """
    Final LangGraph node.

    Reviews the complete workflow for safety.
    Creates escalations if required.
    Logs safety audit.
    """

    state["current_step"] = "safety"

    # ----------------------------------------------------------
    # Gather workflow context
    # ----------------------------------------------------------

    original_messages = state.get("messages", [])

    user_request = ""

    for msg in reversed(original_messages):
        if isinstance(msg, HumanMessage):
            user_request = msg.content
            break

    coordinator = state.get("agent_outputs", {}).get("coordinator", {})
    routing = state.get("agent_outputs", {}).get("routing", {})
    appointment = state.get("agent_outputs", {}).get("appointment", {})
    document = state.get("agent_outputs", {}).get("document", {})
    followup = state.get("agent_outputs", {}).get("followup", {})

    thread_id = state.get("thread_id", "unknown")

    # ----------------------------------------------------------
    # EARLY RETURN
    # Skip LLM if workflow is obviously safe
    # ----------------------------------------------------------

    escalation_required = followup.get("escalation_required", False)

    if (
        state.get("error") is None
        and appointment.get("status") == "success"
        and escalation_required is False
    ):

        result = {
            "safety_passed": True,
            "escalations_created": [],
            "summary": "Workflow passed automatic safety review."
        }

        state["agent_outputs"]["safety"] = result

        return state

    # ----------------------------------------------------------
    # Build prompt
    # ----------------------------------------------------------

    system_content = (
        SAFETY_SYSTEM_PROMPT
        + f"\n\nWorkflow ID: {thread_id}"
        + f"\nPatient request:\n{user_request}"
        + f"\nCoordinator:\n{json.dumps(coordinator)}"
        + f"\nRouting:\n{json.dumps(routing)}"
        + f"\nAppointment:\n{json.dumps(appointment)}"
        + f"\nDocument:\n{json.dumps(document)}"
        + f"\nFollow-up:\n{json.dumps(followup)}"
    )

    messages = [
        SystemMessage(content=system_content),
        HumanMessage(
            content="Perform the final safety review."
        ),
    ]

    llm = get_llm()
    llm_with_tools = llm.bind_tools(SAFETY_TOOLS)

    tool_calls_log = []

    # ----------------------------------------------------------
    # Tool-calling loop
    # ----------------------------------------------------------

    try:

        ai_msg = llm_with_tools.invoke(messages)
        messages.append(ai_msg)

        while ai_msg.tool_calls:

            for tool_call in ai_msg.tool_calls:

                tool_name = tool_call["name"]
                args = tool_call["args"]

                print("\n========== SAFETY TOOL CALL ==========")
                print("Tool:", tool_name)
                print("Args:", args)
                print("======================================\n")

                if tool_name == "create_escalation":
                    result = create_escalation.invoke(args)

                elif tool_name == "log_safety_audit":
                    result = log_safety_audit.invoke(args)

                else:
                    result = f"Unknown tool: {tool_name}"

                tool_calls_log.append(
                    {
                        "tool": tool_name,
                        "status": "success",
                        "arguments": args,
                    }
                )

                messages.append(
                    ToolMessage(
                        content=str(result),
                        tool_call_id=tool_call["id"],
                    )
                )

            ai_msg = llm_with_tools.invoke(messages)
            messages.append(ai_msg)

    except Exception as e:

        state["error"] = f"Safety agent error: {e}"

        state["agent_outputs"]["safety"] = {
            "safety_passed": False,
            "escalations_created": [],
            "summary": f"Safety agent error: {e}",
        }

        return state

    # ----------------------------------------------------------
    # Parse final JSON
    # ----------------------------------------------------------

    try:

        content = ai_msg.content or ""

        if "```" in content:
            content = (
                content
                .replace("```json", "")
                .replace("```", "")
                .strip()
            )

        match = re.search(
            r"\{.*\}",
            content,
            re.DOTALL,
        )

        if not match:
            raise ValueError(
                f"No JSON object found.\n\nLLM Response:\n{content}"
            )

        result = json.loads(match.group(0))

    except Exception as e:

        result = {
            "safety_passed": False,
            "escalations_created": [],
            "summary": f"Could not parse safety output: {e}",
        }

    # ----------------------------------------------------------
    # Optional: Save tool history for debugging only
    # ----------------------------------------------------------

    state.setdefault("tool_history", {})
    state["tool_history"]["safety"] = tool_calls_log

    # ----------------------------------------------------------
    # Save final output
    # ----------------------------------------------------------

    state["agent_outputs"]["safety"] = result

    # ----------------------------------------------------------
    # Final audit log
    # ----------------------------------------------------------

    try:
        log_safety_audit.invoke(
            {
                "workflow_run_id": thread_id,
                "description": (
                    f"Safety review completed. "
                    f"Passed={result.get('safety_passed')}"
                ),
            }
        )
    except Exception:
        pass

    return state