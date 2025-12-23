# LLM Provider Switching

## Overview

The DNP Population Module now supports multiple LLM providers, allowing users to switch between different AI models:

1. **Claude (Anthropic)** - Latest Claude Sonnet 4.5 model
2. **Azure OpenAI (DNP Official)** - DNP's official Azure OpenAI deployment with GPT-4o

## Features

- **Dynamic Provider Selection**: Users can switch between available LLM providers in real-time via a dropdown in the chat interface
- **Auto-Detection**: The system automatically detects which providers are configured and only shows available options
- **Default Priority**: If both providers are configured, Azure OpenAI (DNP) is used as the default
- **Per-Message Provider**: Each chat message can use a different provider (though typically you'll stick with one per conversation)

## Configuration

### Environment Variables

Add the following to your `.env` file:

```bash
# Claude (Anthropic) - Latest AI model
ANTHROPIC_API_KEY=your-anthropic-api-key

# Azure OpenAI (DNP Official) - Preferred for production
AZURE_OPENAI_API_KEY=your-azure-api-key
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT=gpt-4o
AZURE_OPENAI_API_VERSION=2024-08-01-preview
```

### Required Configuration

**At least one** provider must be configured:
- Either `ANTHROPIC_API_KEY`
- Or both `AZURE_OPENAI_API_KEY` and `AZURE_OPENAI_ENDPOINT`

### DNP Azure OpenAI Credentials

For DNP users, use these credentials:

```bash
AZURE_OPENAI_API_KEY=<your-azure-openai-api-key>
AZURE_OPENAI_ENDPOINT=https://dnp-oai-obdies-dev.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT=gpt-4o
AZURE_OPENAI_API_VERSION=2024-08-01-preview
```

## Usage

### Frontend (Chat Interface)

When using the chat interface:

1. Navigate to the **Chat** page
2. Look for the **"Modelo LLM"** dropdown in the header (only appears if multiple providers are configured)
3. Select your preferred provider:
   - **Azure OpenAI (DNP)** - 🇨🇴 DNP Official
   - **Claude (Anthropic)** - 🤖 Claude Sonnet 4.5
4. Send your message - it will use the selected provider

### API Usage

When calling the `/api/v1/chats/query` endpoint:

```json
{
  "query": "¿Cuál es la población de Medellín?",
  "chat_id": 1,
  "provider": "azure_openai"  // or "claude"
}
```

**Provider values:**
- `"azure_openai"` - Use Azure OpenAI (DNP)
- `"claude"` - Use Claude (Anthropic)
- `null` or omitted - Use default provider (Azure OpenAI if configured, otherwise Claude)

### Get Available Providers

```bash
GET /api/v1/chats/providers
```

Response:
```json
{
  "available": ["azure_openai", "claude"],
  "default": "azure_openai"
}
```

## Architecture

### Backend Components

1. **`app/services/llm_provider.py`**
   - `LLMProvider` enum: Defines available providers
   - `LLMProviderService`: Manages provider configuration, validation, and selection

2. **`app/agents/population_agent.py`**
   - Updated to accept `provider` parameter
   - Creates appropriate agent instance based on provider

3. **`app/agents/visualization_agent.py`**
   - Updated to accept `provider` parameter
   - Creates appropriate agent instance based on provider

4. **`app/api/v1/endpoints/chat.py`**
   - `/providers` endpoint: Returns available providers
   - Updated `/query` endpoint: Accepts provider parameter
   - Agent caching: Maintains separate agent instances per provider

### Frontend Components

1. **`frontend/src/app/chat/page.tsx`**
   - Loads available providers on mount
   - Manages selected provider state
   - Passes provider to ChatInterface

2. **`frontend/src/components/ChatInterface.tsx`**
   - Displays provider selector dropdown
   - Shows provider-specific badges and indicators
   - Disables selector during message processing

## Provider Details

### Claude (Anthropic)

- **Model**: `claude-sonnet-4-5-20250929`
- **Strengths**: Latest AI capabilities, excellent reasoning, long context window
- **Use Case**: Development, testing, advanced queries

### Azure OpenAI (DNP)

- **Model**: `gpt-4o`
- **Strengths**: Official DNP deployment, reliable, cost-controlled
- **Use Case**: Production, official DNP usage, compliance requirements

## Troubleshooting

### Provider Not Showing in Dropdown

- Check that environment variables are properly set in `.env`
- Restart the backend after updating `.env`
- Check backend logs for configuration errors

### "Provider configuration error" Message

- Verify API keys are valid and not expired
- For Azure: Ensure both `AZURE_OPENAI_API_KEY` and `AZURE_OPENAI_ENDPOINT` are set
- Check endpoint URLs are correct (no trailing slashes issues)

### Messages Failing with One Provider

- Try switching to the other provider
- Check API key quotas and rate limits
- Review backend logs for specific error messages

## Testing

Test both providers:

```bash
# Test Azure OpenAI
curl -X POST http://localhost:8000/api/v1/chats/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "¿Cuál es la población de Bogotá?",
    "chat_id": 1,
    "provider": "azure_openai"
  }'

# Test Claude
curl -X POST http://localhost:8000/api/v1/chats/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "¿Cuál es la población de Medellín?",
    "chat_id": 1,
    "provider": "claude"
  }'
```

## Future Enhancements

Potential improvements:
- Add more providers (Google Gemini, Cohere, etc.)
- Provider-specific model selection (e.g., GPT-4 vs GPT-3.5)
- Cost tracking per provider
- Performance metrics comparison
- Provider recommendation based on query type
