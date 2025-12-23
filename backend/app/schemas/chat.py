"""Chat schemas for API request/response validation."""
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Dict, Any, List
from app.services.llm_provider import LLMProvider


class ChatBase(BaseModel):
    """Base chat schema."""
    title: str


class ChatCreate(ChatBase):
    """Schema for creating a new chat."""
    pass


class Chat(ChatBase):
    """Schema for chat response."""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class MessageBase(BaseModel):
    """Base message schema."""
    content: str
    role: str
    message_metadata: Optional[Dict[str, Any]] = None


class MessageCreate(MessageBase):
    """Schema for creating a new message."""
    chat_id: int


class Message(MessageBase):
    """Schema for message response."""
    id: int
    chat_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class ChatQuery(BaseModel):
    """Schema for processing a chat query."""
    query: str
    chat_id: int
    provider: Optional[str] = None  # "claude" or "azure_openai"


class ChatResponse(BaseModel):
    """Schema for chat query response."""
    message: str
    sql_query: Optional[str] = None
    visualizations: Optional[List[Dict[str, Any]]] = None
    data: Optional[Any] = None
