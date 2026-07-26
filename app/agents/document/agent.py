"""
Document Agent node that processes uploaded documents.
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
from app.agents.document.prompt import DOCUMENT_SYSTEM_PROMPT

from app.tools.document_tools import (
    list_patient_documents,
    extract_document_text,
    classify_document,
    check_duplicate,
)


DOCUMENT_TOOLS = [
    list_patient_documents,
    extract_document_text,
    classify_document,
    check_duplicate,
]


def document_node(state: AgentCareState) -> AgentCareState:
    """
    LangGraph node responsible for processing uploaded documents.
    """

    state["current_step"] = "document"

    coordinator_plan = (
        state.get("agent_outputs", {})
        .get("coordinator", {})
        .get("plan", {})
    )

    routing = (
        state.get("agent_outputs", {})
        .get("routing", {})
    )

    patient_id = state.get("patient_id", "")

    # Skip if document processing is not required
    if coordinator_plan.get("intent_category") != "upload_document":

        state["agent_outputs"]["document"] = {
            "result": {
                "processed_documents": [],
                "message": "No document processing required."
            },
            "tool_calls": [],
        }

        return state

    # Recover original user request
    user_request = "Process uploaded documents"

    for msg in reversed(state.get("messages", [])):
        if isinstance(msg, HumanMessage):
            user_request = msg.content
            break

    system_content = (
        DOCUMENT_SYSTEM_PROMPT
        + f"\n\nPatient ID: {patient_id}"
        + f"\nCoordinator Plan:\n{json.dumps(coordinator_plan)}"
        + f"\nRouting Decision:\n{json.dumps(routing)}"
    )

    messages = [
        SystemMessage(content=system_content),
        HumanMessage(content=user_request),
    ]

    executed_tools = []

    llm = get_llm()
    llm_with_tools = llm.bind_tools(DOCUMENT_TOOLS)

    try:

        ai_msg = llm_with_tools.invoke(messages)
        messages.append(ai_msg)

        while ai_msg.tool_calls:

            for tool_call in ai_msg.tool_calls:

                tool_name = tool_call["name"]
                args = tool_call["args"]

                try:

                    if tool_name == "list_patient_documents":
                        result = list_patient_documents.invoke(args)

                    elif tool_name == "extract_document_text":
                        result = extract_document_text.invoke(args)

                    elif tool_name == "classify_document":
                        result = classify_document.invoke(args)

                    elif tool_name == "check_duplicate":
                        result = check_duplicate.invoke(args)

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

                    result = f"Tool execution failed: {tool_error}"

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

        state["error"] = f"Document agent error: {e}"

        state["agent_outputs"]["document"] = {
            "result": {
                "processed_documents": [],
                "message": f"Agent error: {e}",
            },
            "tool_calls": executed_tools,
        }

        return state

    # Parse final JSON from LLM
    try:

        content = ai_msg.content or ""

        # Remove markdown fences if present
        if "```" in content:
            content = content.replace("```json", "")
            content = content.replace("```", "")
            content = content.strip()

        # Extract JSON object
        match = re.search(r"\{.*\}", content, re.DOTALL)

        if not match:
            raise ValueError(
                f"No JSON object found.\nLLM output:\n{content}"
            )

        result = json.loads(match.group())

    except Exception as e:

        result = {
            "processed_documents": [],
            "message": f"Could not parse LLM output: {e}",
        }

    state["agent_outputs"]["document"] = {
        "result": result,
        "tool_calls": executed_tools,
    }

    return state