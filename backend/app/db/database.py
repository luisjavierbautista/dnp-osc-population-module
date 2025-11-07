"""
Configuración de la base de datos PostgreSQL con SQLModel.
"""
from sqlmodel import create_engine, Session, SQLModel
from ..core.config import settings

# Crear el engine de SQLAlchemy
engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_pre_ping=True,
    pool_size=settings.MAX_CONNECTIONS_COUNT,
    max_overflow=settings.MIN_CONNECTIONS_COUNT,
)


def init_db() -> None:
    """
    Inicializa las tablas de la base de datos.
    """
    SQLModel.metadata.create_all(engine)


def get_session():
    """
    Generador de sesiones de base de datos para dependency injection.
    """
    with Session(engine) as session:
        yield session
