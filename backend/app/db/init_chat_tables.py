"""
Initialize chat tables in the database.
Run this script to create the chat and chat_messages tables.
"""
from sqlmodel import SQLModel
from app.db.database import engine
from app.models.chat import Chat, ChatMessage


def init_chat_tables():
    """Create chat tables in the database."""
    print("Creating chat tables...")

    # Import all models to ensure they're registered
    from app.models import chat

    # Create tables
    SQLModel.metadata.create_all(engine, tables=[Chat.__table__, ChatMessage.__table__])

    print("✓ Chat tables created successfully!")
    print("  - chats")
    print("  - chat_messages")


if __name__ == "__main__":
    init_chat_tables()
