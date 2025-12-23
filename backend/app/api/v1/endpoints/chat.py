"""Chat endpoints for the LLM chatbot."""
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from sqlalchemy import text
from typing import List, Any
from decimal import Decimal

from app.db.database import get_session
from app.models.chat import Chat, ChatMessage
from app.schemas.chat import (
    ChatCreate,
    Chat as ChatSchema,
    MessageCreate,
    Message as MessageSchema,
    ChatQuery,
    ChatResponse
)
from app.agents.population_agent import PopulationAgent
from app.agents.visualization_agent import VisualizationAgent
from app.core.config import settings
from app.services.llm_provider import LLMProvider, LLMProviderService

router = APIRouter()

# Cache for agents by provider
_agents_cache = {}


def get_agents(provider: LLMProvider = None):
    """
    Initialize agents for a specific provider.

    Args:
        provider: The LLM provider to use. If None, uses default.

    Returns:
        Tuple of (PopulationAgent, VisualizationAgent)
    """
    global _agents_cache

    # Use default provider if none specified
    if provider is None:
        provider = LLMProviderService.get_default_provider()

    if provider is None:
        raise HTTPException(
            status_code=503,
            detail="Chatbot service unavailable: No LLM API keys configured. Please set ANTHROPIC_API_KEY or AZURE_OPENAI_API_KEY in environment variables."
        )

    # Validate provider configuration
    is_valid, error_msg = LLMProviderService.validate_provider(provider)
    if not is_valid:
        raise HTTPException(status_code=503, detail=f"Provider configuration error: {error_msg}")

    # Check cache
    if provider not in _agents_cache:
        # Get model name for the provider
        model_name = LLMProviderService.get_model_name(provider)

        # Create agents with the provider
        _agents_cache[provider] = (
            PopulationAgent(model_name=model_name, provider=provider),
            VisualizationAgent(model_name=model_name, provider=provider)
        )

    return _agents_cache[provider]


def convert_decimals(obj: Any) -> Any:
    """
    Recursively convert Decimal objects to float for JSON serialization.
    PostgreSQL NUMERIC columns return Decimal objects which cannot be JSON serialized.
    """
    if isinstance(obj, Decimal):
        return float(obj)
    elif isinstance(obj, dict):
        return {key: convert_decimals(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_decimals(item) for item in obj]
    else:
        return obj


@router.post("/", response_model=ChatSchema)
async def create_chat(chat: ChatCreate, db: Session = Depends(get_session)):
    """Create a new chat session."""
    db_chat = Chat(**chat.model_dump())
    db.add(db_chat)
    db.commit()
    db.refresh(db_chat)
    return db_chat


@router.get("/", response_model=List[ChatSchema])
async def get_chats(skip: int = 0, limit: int = 100, db: Session = Depends(get_session)):
    """Get all chat sessions."""
    statement = select(Chat).offset(skip).limit(limit).order_by(Chat.created_at.desc())
    chats = db.exec(statement).all()
    return chats


@router.get("/providers")
async def get_available_providers():
    """Get list of available LLM providers."""
    available = LLMProviderService.get_available_providers()
    default = LLMProviderService.get_default_provider()

    return {
        "available": [p.value for p in available],
        "default": default.value if default else None
    }


@router.get("/{chat_id}", response_model=ChatSchema)
async def get_chat(chat_id: int, db: Session = Depends(get_session)):
    """Get a specific chat session."""
    chat = db.get(Chat, chat_id)
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    return chat


@router.get("/{chat_id}/messages", response_model=List[MessageSchema])
async def get_chat_messages(chat_id: int, db: Session = Depends(get_session)):
    """Get all messages for a chat."""
    statement = select(ChatMessage).where(ChatMessage.chat_id == chat_id).order_by(ChatMessage.created_at)
    messages = db.exec(statement).all()
    return messages


async def generate_chat_title(query: str) -> str:
    """Generate a concise title for the chat based on the first question."""
    try:
        population_agent, _ = get_agents()

        # Use the population agent to generate a title
        prompt = f"""Genera un título conciso (máximo 5-6 palabras) para una conversación que comienza con esta pregunta:

        "{query}"

        El título debe estar en español y capturar el tema principal de la pregunta sobre datos de población.
        Retorna SOLO el texto del título, nada más.

        Ejemplos:
        - "¿Cuál es la población de Medellín en 2025?" -> "Población de Medellín 2025"
        - "Muéstrame la pirámide poblacional de Bogotá" -> "Pirámide poblacional Bogotá"
        - "¿Cómo ha evolucionado la población de Cali?" -> "Evolución población Cali"
        """

        result = await population_agent.agent.run(prompt)
        title = result.output.strip().strip('"').strip("'")

        # Limit title length
        if len(title) > 60:
            title = title[:57] + "..."

        return title
    except:
        # Fallback to truncated query
        return query[:50] + "..." if len(query) > 50 else query


@router.post("/query", response_model=ChatResponse)
async def process_query(query: ChatQuery, db: Session = Depends(get_session)):
    """Process a natural language query about population data."""
    try:
        # Parse provider from query
        provider = None
        if query.provider:
            try:
                provider = LLMProvider(query.provider)
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid provider: {query.provider}. Must be 'claude' or 'azure_openai'"
                )

        # Get agents for the selected provider
        population_agent, viz_agent = get_agents(provider)

        # Check if this is the first message in the chat
        statement = select(ChatMessage).where(ChatMessage.chat_id == query.chat_id)
        messages = db.exec(statement).all()
        is_first_message = len(messages) == 0

        # Save user message
        user_message = ChatMessage(
            chat_id=query.chat_id,
            role="user",
            content=query.query
        )
        db.add(user_message)
        db.commit()

        # Generate chat title if this is the first message
        if is_first_message:
            chat = db.get(Chat, query.chat_id)
            if chat:
                new_title = await generate_chat_title(query.query)
                chat.title = new_title
                db.commit()

        # Convert natural language to SQL
        sql_result = await population_agent.natural_language_to_sql(query.query)

        # Execute the SQL query
        from app.db.database import engine
        with engine.connect() as conn:
            result = conn.execute(text(sql_result.query))
            data = [convert_decimals(dict(row._mapping)) for row in result]

        # Generate visualizations
        viz_response = await viz_agent.create_visualizations(data, query.query)

        # Prepare response
        response = ChatResponse(
            message=viz_response.summary,
            sql_query=sql_result.query,
            visualizations=viz_response.visualizations,
            data=data[:5000]  # Limit data size in response to prevent excessive payload
        )

        # Save assistant message with converted metadata
        metadata = {
            "sql_query": sql_result.query,
            "visualizations": viz_response.visualizations,
            "data_count": len(data)
        }
        # Convert Decimal objects to float for JSON serialization
        metadata = convert_decimals(metadata)

        assistant_message = ChatMessage(
            chat_id=query.chat_id,
            role="assistant",
            content=response.message,
            message_metadata=metadata
        )
        db.add(assistant_message)
        db.commit()

        return response

    except Exception as e:
        # Save error message
        error_message = ChatMessage(
            chat_id=query.chat_id,
            role="assistant",
            content=f"Error procesando consulta: {str(e)}"
        )
        db.add(error_message)
        db.commit()

        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{chat_id}")
async def delete_chat(chat_id: int, db: Session = Depends(get_session)):
    """Delete a chat and all its messages."""
    # Get chat
    chat = db.get(Chat, chat_id)
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")

    # Delete messages first (cascade should handle this but being explicit)
    statement = select(ChatMessage).where(ChatMessage.chat_id == chat_id)
    messages = db.exec(statement).all()
    for message in messages:
        db.delete(message)

    # Delete chat
    db.delete(chat)
    db.commit()

    return {"message": "Chat deleted successfully"}
