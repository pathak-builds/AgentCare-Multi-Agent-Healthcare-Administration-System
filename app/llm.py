"""
Provides a singleton ChatGroq instance.
"""
from langchain_groq import ChatGroq
from app.config import settings

def get_llm() -> ChatGroq:
    """Return a ChatGroq LLM configured with the application model."""
    return ChatGroq(
        groq_api_key=settings.groq_api_key,
        model=settings.model_name,
        temperature=0,
    )