"""
Follow-up Agent node: creates reminders and logs follow-up actions.
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
from app.agents.followup.prompt import FOLLOWUP_SYSTEM_PROMPT

from app.tools.followup_tools import (
    get_appointments_without_reminders,
    create_reminder,
    log_followup_action,
)

FOLLOWUP_TOOLS = [
    get_appointments_without_reminders,
    create_reminder,
    log_followup_action,
]


def followup_node(state: AgentCareState) -> AgentCareState:
    """
    LangGraph node responsible for:

    • Creating appointment reminders
    • Logging follow-up actions
    • Flagging incomplete workflows
    """

    state["current_step"] = "followup"

    coordinator_plan = (
        state.get("agent_outputs", {})
        .get("coordinator", {})
        .get("plan", {})
    )

    appointment_output = (
        state.get("agent_outputs", {})
        .get("appointment", {})
    )

    document_output = (
        state.get("agent_outputs", {})
        .get("document", {})
    )

    patient_id = state.get("patient_id", "")
    intent = state.get("intent", "")
    workflow_id = state.get("thread_id", "unknown")
    # ------------------------------------------------------------------
    # Early exit if this workflow does not require follow-up
    # ------------------------------------------------------------------

    appointment_success = (
        appointment_output.get("status") == "success"
    )

    document_processed = (
        bool(document_output.get("result", {}).get("processed_documents"))
    )

    if (
        not appointment_success
        and not document_processed
        and intent not in ["book_appointment", "upload_document"]
    ):
        state["agent_outputs"]["followup"] = {
            "result": {
                "reminders_created": [],
                "followup_actions": [],
                "escalation_required": False,
                "workflow_complete": True,
                "summary": "No follow-up required."
            },
            "tool_calls": [],
        }

        return state

    # ------------------------------------------------------------------
    # Build prompt
    # ------------------------------------------------------------------

    system_content = (
        FOLLOWUP_SYSTEM_PROMPT
        + f"\n\nPatient ID: {patient_id}"
        + f"\nCoordinator plan:\n{json.dumps(coordinator_plan)}"
        + f"\nAppointment output:\n{json.dumps(appointment_output)}"
        + f"\nDocument output:\n{json.dumps(document_output)}"
    )

    messages = [
        SystemMessage(content=system_content),
        HumanMessage(
            content="Process follow-up tasks based on the completed workflow."
        ),
    ]

    executed_tools = []

    llm = get_llm()
    llm_with_tools = llm.bind_tools(FOLLOWUP_TOOLS)

    # ------------------------------------------------------------------
    # Tool loop
    # ------------------------------------------------------------------

    try:

        ai_msg = llm_with_tools.invoke(messages)
        messages.append(ai_msg)

        while ai_msg.tool_calls:

            for tool_call in ai_msg.tool_calls:

                tool_name = tool_call["name"]
                args = tool_call["args"]

                try:

                    if tool_name == "get_appointments_without_reminders":

                        result = get_appointments_without_reminders.invoke(args)

                    elif tool_name == "create_reminder":

                        result = create_reminder.invoke(args)

                    elif tool_name == "log_followup_action":

                        result = log_followup_action.invoke(args)

                    else:

                        result = f"Unknown tool: {tool_name}"

                    executed_tools.append(
                        {
                            "tool": tool_name,
                            "status": "success",
                            "arguments": args,
                        }
                    )

                except Exception as tool_error:

                    result = f"Tool failed: {tool_error}"

                    executed_tools.append(
                        {
                            "tool": tool_name,
                            "status": "failed",
                            "arguments": args,
                            "error": str(tool_error),
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

        state["error"] = f"Follow-up agent error: {e}"

        state["agent_outputs"]["followup"] = {
            "result": {
                "reminders_created": [],
                "followup_actions": [],
                "escalation_required": True,
                "workflow_complete": False,
                "summary": f"Agent error: {e}",
            },
            "tool_calls": executed_tools,
        }

        return state

    # ------------------------------------------------------------------
    # Parse final JSON
    # ------------------------------------------------------------------

    try:

        content = ai_msg.content or ""

        if "```" in content:
            content = content.replace("```json", "")
            content = content.replace("```", "")
            content = content.strip()

        match = re.search(r"\{.*\}", content, re.DOTALL)

        if not match:
            raise ValueError(
                f"No JSON object found.\nLLM Response:\n{content}"
            )

        result = json.loads(match.group())

    except Exception as e:

        result = {
            "reminders_created": [],
            "followup_actions": [],
            "escalation_required": False,
            "workflow_complete": False,
            "summary": f"Could not parse LLM output: {e}",
        }

    # ------------------------------------------------------------------
    # Save result
    # ------------------------------------------------------------------

    state["agent_outputs"]["followup"] = {
        "result": result,
        "tool_calls": executed_tools,
    }

    return state