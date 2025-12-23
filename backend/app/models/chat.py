"""Chat models for LLM chatbot functionality."""
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime
from sqlalchemy import Column, JSON


class Chat(SQLModel, table=True):
    """Chat session model."""
    __tablename__ = "chats"

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(max_length=255, nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default=None, sa_column_kwargs={"onupdate": datetime.utcnow})

    # Relationship
    messages: List["ChatMessage"] = Relationship(back_populates="chat", sa_relationship_kwargs={"cascade": "all, delete-orphan"})


class ChatMessage(SQLModel, table=True):
    """Chat message model."""
    __tablename__ = "chat_messages"

    id: Optional[int] = Field(default=None, primary_key=True)
    chat_id: int = Field(foreign_key="chats.id", index=True)
    role: str = Field(max_length=50, nullable=False)  # 'user' or 'assistant'
    content: str = Field(nullable=False)
    message_metadata: Optional[dict] = Field(default=None, sa_column=Column(JSON))  # For storing visualizations, queries, etc.
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationship
    chat: Optional["Chat"] = Relationship(back_populates="messages")
