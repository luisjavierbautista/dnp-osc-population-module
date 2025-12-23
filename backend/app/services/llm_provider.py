"""LLM Provider Service for managing different LLM backends."""
from enum import Enum
from typing import Optional
from openai import AsyncAzureOpenAI
from app.core.config import settings


class LLMProvider(str, Enum):
    """Available LLM providers."""
    CLAUDE = "claude"
    AZURE_OPENAI = "azure_openai"


class LLMProviderService:
    """Service for managing and switching between LLM providers."""

    @staticmethod
    def get_model_name(provider: LLMProvider) -> str:
        """
        Get the model name/identifier for pydantic-ai based on the provider.

        Args:
            provider: The LLM provider to use

        Returns:
            Model name string compatible with pydantic-ai
        """
        if provider == LLMProvider.CLAUDE:
            # Use the latest Claude Sonnet 4.5 model
            return "anthropic:claude-sonnet-4-5-20250929"
        elif provider == LLMProvider.AZURE_OPENAI:
            # For Azure OpenAI, we use a custom client approach
            # The model name will be set when creating the agent
            return "azure_openai"
        else:
            raise ValueError(f"Unknown provider: {provider}")

    @staticmethod
    def validate_provider(provider: LLMProvider) -> tuple[bool, Optional[str]]:
        """
        Validate that the provider is properly configured with required credentials.

        Args:
            provider: The LLM provider to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        if provider == LLMProvider.CLAUDE:
            if not settings.ANTHROPIC_API_KEY or not settings.ANTHROPIC_API_KEY.strip():
                return False, "Claude API key not configured. Please set ANTHROPIC_API_KEY."
            return True, None

        elif provider == LLMProvider.AZURE_OPENAI:
            if not settings.AZURE_OPENAI_API_KEY or not settings.AZURE_OPENAI_API_KEY.strip():
                return False, "Azure OpenAI API key not configured. Please set AZURE_OPENAI_API_KEY."
            if not settings.AZURE_OPENAI_ENDPOINT or not settings.AZURE_OPENAI_ENDPOINT.strip():
                return False, "Azure OpenAI endpoint not configured. Please set AZURE_OPENAI_ENDPOINT."
            return True, None

        return False, f"Unknown provider: {provider}"

    @staticmethod
    def get_available_providers() -> list[LLMProvider]:
        """
        Get list of currently available (configured) providers.

        Returns:
            List of configured providers
        """
        available = []

        # Check Claude/Anthropic
        if settings.ANTHROPIC_API_KEY and settings.ANTHROPIC_API_KEY.strip():
            available.append(LLMProvider.CLAUDE)

        # Check Azure OpenAI
        if (settings.AZURE_OPENAI_API_KEY and settings.AZURE_OPENAI_API_KEY.strip() and
            settings.AZURE_OPENAI_ENDPOINT and settings.AZURE_OPENAI_ENDPOINT.strip()):
            available.append(LLMProvider.AZURE_OPENAI)

        return available

    @staticmethod
    def get_azure_client() -> AsyncAzureOpenAI:
        """
        Create and return an Azure OpenAI client.

        Returns:
            Configured AsyncAzureOpenAI client
        """
        return AsyncAzureOpenAI(
            api_key=settings.AZURE_OPENAI_API_KEY,
            azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
            api_version=settings.AZURE_OPENAI_API_VERSION,
        )

    @staticmethod
    def get_default_provider() -> Optional[LLMProvider]:
        """
        Get the default provider based on available configuration.
        Prioritizes Azure OpenAI (DNP) if available, then Claude.

        Returns:
            Default provider or None if none available
        """
        available = LLMProviderService.get_available_providers()

        if not available:
            return None

        # Prefer Azure OpenAI (DNP) first
        if LLMProvider.AZURE_OPENAI in available:
            return LLMProvider.AZURE_OPENAI

        # Then Claude
        if LLMProvider.CLAUDE in available:
            return LLMProvider.CLAUDE

        return available[0] if available else None
