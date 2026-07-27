"""
Unit tests for LangGraph agent nodes.
"""

import json
from unittest.mock import MagicMock, patch

import pytest
from langchain_core.messages import AIMessage, HumanMessage

from app.workflow.state import AgentCareState
from app.agents.coordinator.agent import coordinator_node
from app.agents.routing.agent import routing_node
from app.agents.appointment.agent import appointment_node
from app.agents.safety.agent import safety_node


# ---------------------------------------------------------------------
# Shared workflow state
# ---------------------------------------------------------------------

@pytest.fixture
def base_state(seed_data):
    return AgentCareState(
        messages=[
            HumanMessage(
                content="Book cardiology appointment"
            )
        ],
        patient_id=seed_data["patient_profile"].id,
        intent="book_appointment",
        current_step="coordinator",
        agent_outputs={},
        error=None,
        thread_id="test-workflow-1",
    )


# ---------------------------------------------------------------------
# Coordinator
# ---------------------------------------------------------------------

def test_coordinator_node(base_state):

    mock_llm = MagicMock()
    mock_llm.bind_tools.return_value = mock_llm

    mock_llm.invoke.return_value = AIMessage(
        content=json.dumps(
            {
                "intent_category": "book_appointment",
                "department": "Cardiology",
                "next_step": "routing",
                "plan_description": "Book cardiologist",
                "requires_escalation": False,
            }
        ),
        tool_calls=[],
    )

    with patch(
        "app.agents.coordinator.agent.get_llm",
        return_value=mock_llm,
    ):

        state = coordinator_node(base_state)

    assert state["error"] is None

    assert (
        state["agent_outputs"]["coordinator"]["plan"]["intent_category"]
        == "book_appointment"
    )

    assert (
        state["agent_outputs"]["coordinator"]["plan"]["department"]
        == "Cardiology"
    )


# ---------------------------------------------------------------------
# Routing
# ---------------------------------------------------------------------

def test_routing_node(base_state, seed_data):

    base_state["agent_outputs"]["coordinator"] = {
        "plan": {
            "intent_category": "book_appointment",
            "department": "Cardiology",
        }
    }

    mock_llm = MagicMock()
    mock_llm.bind_tools.return_value = mock_llm

    mock_llm.invoke.side_effect = [

        AIMessage(
            content="",
            tool_calls=[
                {
                    "name": "department_list",
                    "args": {},
                    "id": "1",
                }
            ],
        ),

        AIMessage(
            content=json.dumps(
                {
                    "department_id": seed_data["department"].id,
                    "department_name": "Cardiology",
                    "confidence": 0.95,
                    "escalation_reason": None,
                }
            ),
            tool_calls=[],
        ),
    ]

    fake_department_tool = MagicMock()
    fake_department_tool.invoke.return_value = [
        {
            "id": seed_data["department"].id,
            "name": "Cardiology",
        }
    ]

    with patch(
        "app.agents.routing.agent.get_llm",
        return_value=mock_llm,
    ), patch(
        "app.agents.routing.agent.department_list",
        fake_department_tool,
    ):

        state = routing_node(base_state)

    assert state["error"] is None

    assert (
        state["agent_outputs"]["routing"]["department_name"]
        == "Cardiology"
    )


# ---------------------------------------------------------------------
# Appointment
# ---------------------------------------------------------------------

def test_appointment_node(base_state):

    base_state["agent_outputs"]["coordinator"] = {
        "plan": {
            "intent_category": "book_appointment"
        }
    }

    base_state["agent_outputs"]["routing"] = {
        "department_id": "dept-id"
    }

    mock_llm = MagicMock()
    mock_llm.bind_tools.return_value = mock_llm

    mock_llm.invoke.side_effect = [

        AIMessage(
            content="",
            tool_calls=[
                {
                    "name": "book_appointment",
                    "args": {
                        "slot_id": "slot-id",
                        "patient_id": base_state["patient_id"],
                        "reason": "",
                        "notes": "",
                    },
                    "id": "1",
                }
            ],
        )
    ]

    fake_booking_tool = MagicMock()

    fake_booking_tool.invoke.return_value = json.dumps(
        {
            "status": "success",
            "appointment_id": "appt-123",
            "slot_id": "slot-id",
            "doctor_id": "doctor-id",
            "appointment_time": "2026-08-01T10:00:00",
            "message": "Appointment booked successfully",
        }
    )

    with patch(
        "app.agents.appointment.agent.get_llm",
        return_value=mock_llm,
    ), patch(
        "app.agents.appointment.agent.book_appointment",
        fake_booking_tool,
    ):

        state = appointment_node(base_state)

    assert state["error"] is None

    assert (
        state["agent_outputs"]["appointment"]["status"]
        == "success"
    )

    assert (
        state["agent_outputs"]["appointment"]["appointment_id"]
        == "appt-123"
    )


# ---------------------------------------------------------------------
# Safety
# ---------------------------------------------------------------------

def test_safety_node_escalation(base_state):

    base_state["messages"] = [
        HumanMessage(
            content="I have chest pain, what medicine should I take?"
        )
    ]

    base_state["agent_outputs"]["coordinator"] = {
        "plan": {
            "requires_escalation": True
        }
    }

    base_state["agent_outputs"]["appointment"] = {
        "status": "failed"
    }

    base_state["agent_outputs"]["followup"] = {
        "escalation_required": True
    }

    mock_llm = MagicMock()
    mock_llm.bind_tools.return_value = mock_llm

    mock_llm.invoke.side_effect = [

        AIMessage(
            content="",
            tool_calls=[
                {
                    "name": "create_escalation",
                    "args": {
                        "workflow_run_id": "test-workflow-1",
                        "reason": "Medical advice request",
                    },
                    "id": "1",
                }
            ],
        ),

        AIMessage(
            content=json.dumps(
                {
                    "safety_passed": False,
                    "escalations_created": [
                        {
                            "id": "esc-1",
                            "reason": "Medical advice request",
                        }
                    ],
                    "summary": "Escalation created",
                }
            ),
            tool_calls=[],
        ),
    ]

    fake_escalation_tool = MagicMock()
    fake_escalation_tool.invoke.return_value = "Escalation created"

    fake_audit_tool = MagicMock()
    fake_audit_tool.invoke.return_value = "Audit logged"

    with patch(
        "app.agents.safety.agent.get_llm",
        return_value=mock_llm,
    ), patch(
        "app.agents.safety.agent.create_escalation",
        fake_escalation_tool,
    ), patch(
        "app.agents.safety.agent.log_safety_audit",
        fake_audit_tool,
    ):

        state = safety_node(base_state)

    assert state["error"] is None

    assert (
        state["agent_outputs"]["safety"]["safety_passed"]
        is False
    )

    assert len(
        state["agent_outputs"]["safety"]["escalations_created"]
    ) == 1