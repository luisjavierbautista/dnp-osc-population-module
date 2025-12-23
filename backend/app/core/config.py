"""
Configuración del módulo de población DNP.
"""
from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import Optional, Union


class Settings(BaseSettings):
    """Configuración de la aplicación."""

    # App
    PROJECT_NAME: str = "Módulo de Población - DNP"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = False

    # Database - DATABASE_URL takes priority (Railway standard)
    DATABASE_URL: Optional[str] = None
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "population_user"
    POSTGRES_PASSWORD: str = "population_pass"
    POSTGRES_DB: str = "population_db"
    POSTGRES_PORT: int = 5432

    def get_database_url(self) -> str:
        # Prioritize DATABASE_URL if set (Railway injects this)
        if self.DATABASE_URL:
            return self.DATABASE_URL
        return (
            f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    # Security
    SECRET_KEY: str = "CHANGE-THIS-SECRET-KEY-IN-PRODUCTION"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # CORS - stored as string, parsed at runtime
    BACKEND_CORS_ORIGINS: str = "http://localhost:3000,http://localhost:3001,http://localhost:3002,http://localhost:3003,http://localhost:8000,https://dnp.ngrok.app,https://dnp-back.ngrok.app"

    @property
    def cors_origins_list(self) -> list[str]:
        """Parse CORS origins from string to list."""
        if isinstance(self.BACKEND_CORS_ORIGINS, list):
            return self.BACKEND_CORS_ORIGINS
        # Handle JSON array format
        if self.BACKEND_CORS_ORIGINS.startswith("["):
            import json
            try:
                return json.loads(self.BACKEND_CORS_ORIGINS)
            except json.JSONDecodeError:
                pass
        # Handle comma-separated format
        return [origin.strip() for origin in self.BACKEND_CORS_ORIGINS.split(",") if origin.strip()]

    # Rate limiting
    RATE_LIMIT_PER_MINUTE: int = 100

    # Performance
    MAX_CONNECTIONS_COUNT: int = 10
    MIN_CONNECTIONS_COUNT: int = 5

    # AI / LLM
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None

    # Azure OpenAI (DNP)
    AZURE_OPENAI_API_KEY: Optional[str] = None
    AZURE_OPENAI_ENDPOINT: Optional[str] = None
    AZURE_OPENAI_DEPLOYMENT: str = "gpt-4o"
    AZURE_OPENAI_API_VERSION: str = "2024-08-01-preview"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
