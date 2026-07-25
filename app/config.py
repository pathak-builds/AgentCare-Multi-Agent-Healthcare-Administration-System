"""
Application configuration using Pydantic Settings.
Loads from .env file and environment variables.
"""

from pydantic_settings import BaseSettings
from pydantic import Field
from pathlib import Path

class Settings(BaseSettings):
    """Global settings for AgentCare."""
    groq_api_key: str = Field(..., env="GROQ_API_KEY")
    database_url: str = Field("sqlite:///./agentcare.db", env="DATABASE_URL")
    jwt_secret: str = Field(..., env="JWT_SECRET")
    model_name: str = Field("llama-3.3-70b-versatile", env="MODEL_NAME")
    chroma_db: str = Field("./chroma_db", env="CHROMA_DB")

    # Base directory of the project
    base_dir: Path = Path(__file__).resolve().parent.parent

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


settings = Settings()