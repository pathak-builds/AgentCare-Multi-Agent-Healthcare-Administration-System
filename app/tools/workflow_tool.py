"""
Tool to check workflow status (simplified for coordinator).
"""
from langchain_core.tools import tool

@tool
def workflow_status(workflow_id: str) -> str:
    """Return the status of a workflow run. Currently returns a placeholder."""
    return f"Workflow {workflow_id} is currently in progress (placeholder)."