"""
Configuración del módulo de población DNP.
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Configuración de la aplicación."""

    # App
    PROJECT_NAME: str = "Módulo de Población - DNP"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = False

    # Database
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "population_user"
    POSTGRES_PASSWORD: str = "population_pass"
    POSTGRES_DB: str = "population_db"
    POSTGRES_PORT: int = 5432

    @property
    def DATABASE_URL(self) -> str:
        return (
            f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    # Security
    SECRET_KEY: str = "CHANGE-THIS-SECRET-KEY-IN-PRODUCTION"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # CORS
    BACKEND_CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:8000"]

    # Rate limiting
    RATE_LIMIT_PER_MINUTE: int = 100

    # Performance
    MAX_CONNECTIONS_COUNT: int = 10
    MIN_CONNECTIONS_COUNT: int = 5

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
