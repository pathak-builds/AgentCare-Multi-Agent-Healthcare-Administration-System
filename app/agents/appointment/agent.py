"""
Appointment Agent node that handles booking, rescheduling, cancellation using real DB tools.
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
from app.agents.appointment.prompt import APPOINTMENT_SYSTEM_PROMPT

from app.tools.doctor_search import doctor_search
from app.tools.slot_search import slot_search
from app.tools.book_appointment import book_appointment
from app.tools.cancel_appointment import cancel_appointment
from app.tools.reschedule_appointment import reschedule_appointment


APPOINTMENT_TOOLS = [
    doctor_search,
    slot_search,
    book_appointment,
    cancel_appointment,
    reschedule_appointment,
]


def appointment_node(state: AgentCareState) -> AgentCareState:
    """
    LangGraph node that manages appointment booking,
    rescheduling and cancellation.
    """

    state["current_step"] = "appointment"

    # --------------------------------------------------------
    # Gather workflow context
    # --------------------------------------------------------

    coordinator_plan = (
        state.get("agent_outputs", {})
        .get("coordinator", {})
        .get("plan", {})
    )

    appointment_intents = {
        "book_appointment",
        "cancel_appointment",
        "reschedule_appointment",
    }

    # Skip appointment node if workflow doesn't need it
    if coordinator_plan.get("intent_category") not in appointment_intents:
        state["agent_outputs"]["appointment"] = {
            "status": "skipped",
            "appointment_id": None,
            "message": "Appointment processing not required for this workflow.",
        }
        return state

    routing = (
        state.get("agent_outputs", {})
        .get("routing", {})
    )

    patient_id = state.get("patient_id", "")
    intent = state.get("intent", "")

    original_messages = state.get("messages", [])

    user_request = intent

    for msg in reversed(original_messages):
        if isinstance(msg, HumanMessage):
            user_request = msg.content
            break

    # --------------------------------------------------------
    # Build prompt
    # --------------------------------------------------------

    system_content = (
        APPOINTMENT_SYSTEM_PROMPT
        + f"\n\nCurrent patient_id: {patient_id}"
        + f"\nRouting decision:\n{json.dumps(routing)}"
        + f"\nCoordinator plan:\n{json.dumps(coordinator_plan)}"
    )

    messages = [
        SystemMessage(content=system_content),
        HumanMessage(content=user_request),
    ]

    llm = get_llm()
    llm_with_tools = llm.bind_tools(APPOINTMENT_TOOLS)

    # --------------------------------------------------------
    # Tool loop
    # --------------------------------------------------------

    try:

        ai_msg = llm_with_tools.invoke(messages)
        messages.append(ai_msg)

        while ai_msg.tool_calls:

            for tool_call in ai_msg.tool_calls:

                tool_name = tool_call["name"]
                args = tool_call["args"]

                print("\n========== APPOINTMENT TOOL CALL ==========")
                print("Tool:", tool_name)
                print("Args:", args)
                print("==========================================\n")

                if tool_name == "doctor_search":
                    result = doctor_search.invoke(args)

                elif tool_name == "slot_search":
                    result = slot_search.invoke(args)

                elif tool_name == "book_appointment":

                    result = book_appointment.invoke(args)

                    # --------------------------------------------------
                    # EARLY RETURN
                    # The booking tool already returns structured JSON.
                    # No need for another expensive LLM call.
                    # --------------------------------------------------

                    try:
                        booking_result = json.loads(result)

                        if booking_result.get("status") == "success":
                            state["agent_outputs"]["appointment"] = booking_result
                            return state

                    except Exception:
                        # If booking failed and returned plain text,
                        # continue the normal LLM loop.
                        pass

                elif tool_name == "cancel_appointment":
                    result = cancel_appointment.invoke(args)

                elif tool_name == "reschedule_appointment":
                    result = reschedule_appointment.invoke(args)

                else:
                    result = f"Unknown tool: {tool_name}"

                messages.append(
                    ToolMessage(
                        content=str(result),
                        tool_call_id=tool_call["id"],
                    )
                )

            ai_msg = llm_with_tools.invoke(messages)
            messages.append(ai_msg)

    except Exception as e:

        state["error"] = f"Appointment agent error: {e}"

        state["agent_outputs"]["appointment"] = {
            "status": "failure",
            "appointment_id": None,
            "message": f"Agent error: {e}",
        }

        return state

    # --------------------------------------------------------
    # Parse final LLM response
    # --------------------------------------------------------

    try:

        content = ai_msg.content or ""

        if "```" in content:
            content = content.replace("```json", "")
            content = content.replace("```", "")
            content = content.strip()

        match = re.search(
            r"\{.*\}",
            content,
            re.DOTALL,
        )

        if not match:
            raise ValueError(
                f"No JSON object found.\nResponse:\n{content}"
            )

        result = json.loads(match.group(0))

    except Exception as e:

        result = {
            "status": "failure",
            "appointment_id": None,
            "message": f"Could not parse final output: {e}",
        }

    state["agent_outputs"]["appointment"] = result

    return state