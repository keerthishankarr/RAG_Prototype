"""
Configuration management using Pydantic BaseSettings.
"""
import os
from pathlib import Path
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # LLM API Keys
    openai_api_key: str = Field(default="", env="OPENAI_API_KEY")

    # Embedding Configuration
    embedding_model: str = Field(default="all-MiniLM-L6-v2", env="EMBEDDING_MODEL")

    # Vector Database
    vector_db_path: str = Field(default="./data/chromadb", env="VECTOR_DB_PATH")

    # Application Database
    database_url: str = Field(default="sqlite:///./data/app.db", env="DATABASE_URL")

    # Default RAG Settings
    default_chunk_size: int = Field(default=500, env="DEFAULT_CHUNK_SIZE")
    default_chunk_overlap: int = Field(default=50, env="DEFAULT_CHUNK_OVERLAP")
    default_top_k: int = Field(default=3, env="DEFAULT_TOP_K")
    default_temperature: float = Field(default=0.7, env="DEFAULT_TEMPERATURE")
    default_model: str = Field(default="gpt-4o", env="DEFAULT_MODEL")
    default_max_tokens: int = Field(default=500, env="DEFAULT_MAX_TOKENS")
    default_min_score: float = Field(default=0.7, env="DEFAULT_MIN_SCORE")
    system_prompt: str = Field(
        default="""You are a helpful assistant that answers questions based on Aesop's Fables.

Use the following context to answer the question. If the answer cannot be found in the context, say so.

Context:
{retrieved_chunks}

Question: {user_query}

Answer:""",
        env="SYSTEM_PROMPT"
    )

    # Server Configuration
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=8000, env="PORT")
    debug: bool = Field(default=True, env="DEBUG")
    cors_origins: str = Field(default="http://localhost:5173", env="CORS_ORIGINS")

    # Directories
    data_dir: str = Field(default="./data", env="DATA_DIR")
    upload_dir: str = Field(default="./data/uploads", env="UPLOAD_DIR")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

    def get_cors_origins_list(self) -> List[str]:
        """Parse CORS origins as a list."""
        return [origin.strip() for origin in self.cors_origins.split(",")]

    def create_directories(self) -> None:
        """Create necessary directories if they don't exist."""
        directories = [
            self.data_dir,
            self.upload_dir,
            self.vector_db_path,
        ]

        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)

    def get_database_path(self) -> str:
        """Get the SQLite database file path."""
        # Extract path from database URL
        if self.database_url.startswith("sqlite:///"):
            return self.database_url.replace("sqlite:///", "")
        return "./data/app.db"


# Global settings instance
_settings = None


def get_settings() -> Settings:
    """Get or create the global settings instance."""
    global _settings
    if _settings is None:
        _settings = Settings()
        _settings.create_directories()
    return _settings
