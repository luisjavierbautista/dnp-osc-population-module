# DNP Population Module - Technical Documentation

## Production Deployment

### Docker Images (Docker Hub)

| Image | Repository |
|-------|------------|
| Backend | `imbautista/dnp-population-backend:latest` |
| Frontend | `imbautista/dnp-population-frontend:latest` |

### Railway Deployment

**Backend URL:** `https://dnp-population-backend-production.up.railway.app`

**Backend Environment Variables:**
```bash
# Database (Railway PostgreSQL)
DATABASE_URL=postgresql://postgres:RHMAVhyrUFdwlCAFYtCETUnwLmmMFEdz@turntable.proxy.rlwy.net:52753/railway

# Security
SECRET_KEY=<your-secret-key>

# CORS
BACKEND_CORS_ORIGINS=https://your-frontend.railway.app,http://localhost:3000

# Azure OpenAI (DNP)
AZURE_OPENAI_API_KEY=<your-azure-openai-api-key>
AZURE_OPENAI_ENDPOINT=https://dnp-oai-obdies-dev.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT=gpt-4o
AZURE_OPENAI_API_VERSION=2024-08-01-preview

# Port
PORT=8000
```

**Frontend Environment Variables:**
```bash
PORT=3000
```
Note: `NEXT_PUBLIC_API_URL` is baked into the frontend image at build time.

### Database

**Production Database (Railway):**
- Host: `turntable.proxy.rlwy.net`
- Port: `52753`
- User: `postgres`
- Database: `railway`

**Data Statistics:**
- `territorio`: 1,156 territories
- `poblacion_edad`: 17.5M+ population records by age
- `poblacion_total`: 87,093 total population records
- `dane_regions`: 23 DANE regions
- Plus fertility, mortality, migration, and growth indicators

### Rebuilding & Deploying

**Backend:**
```bash
# Build and push
cd /path/to/project
docker compose build backend
docker tag dnp-osc-population-module-backend:latest imbautista/dnp-population-backend:latest
docker push imbautista/dnp-population-backend:latest
```

**Frontend:**
```bash
# Build with production API URL baked in
cd frontend
docker build -f Dockerfile.prod \
  --build-arg NEXT_PUBLIC_API_URL=https://dnp-population-backend-production.up.railway.app/api/v1 \
  -t imbautista/dnp-population-frontend:latest .
docker push imbautista/dnp-population-frontend:latest
```

**Database Migration (Local to Railway):**
```bash
# Dump local database
PGPASSWORD=population_pass pg_dump -h localhost -p 5434 -U population_user -d population_db \
  --no-owner --no-acl -F c -f /tmp/dnp_backup.dump

# Restore to Railway
PGPASSWORD=RHMAVhyrUFdwlCAFYtCETUnwLmmMFEdz pg_restore \
  -h turntable.proxy.rlwy.net -p 52753 -U postgres -d railway \
  --no-owner --no-acl --clean --if-exists /tmp/dnp_backup.dump
```

---

# Claude & Azure OpenAI Integration - Technical Documentation

## Overview

This document provides technical details about the LLM provider switching implementation, specifically focusing on the integration with Claude (Anthropic) and Azure OpenAI for the DNP Population Module.

## Implementation Summary

Successfully implemented dual LLM provider support allowing users to switch between:
- **Claude Sonnet 4.5** (Anthropic)
- **Azure OpenAI GPT-4o** (DNP Production)

## Technical Challenge & Solution

### The Azure OpenAI Challenge

Initially, integrating Azure OpenAI with pydantic-ai (the agent framework used) was challenging because:

1. **Standard approach didn't work**: Setting environment variables like `OPENAI_API_TYPE=azure` or `OPENAI_API_BASE` didn't work with pydantic-ai v1.14.0
2. **Custom client approach failed**: Attempting to pass a custom `AsyncAzureOpenAI` client resulted in: `UserError: Unknown keyword arguments: 'openai_client'`
3. **Model prefix confusion**: Tried prefixes like `azure-openai:`, `azureopenai:`, but got: `ValueError: Unknown provider: azure-openai`

### The Solution ✅

pydantic-ai has **built-in Azure OpenAI support** through the `OpenAIChatModel` class with a `provider='azure'` parameter.

#### Working Implementation

```python
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIChatModel
from app.core.config import settings
import os

# Step 1: Set required environment variables
os.environ["OPENAI_API_VERSION"] = settings.AZURE_OPENAI_API_VERSION
os.environ["AZURE_OPENAI_ENDPOINT"] = settings.AZURE_OPENAI_ENDPOINT
os.environ["AZURE_OPENAI_API_KEY"] = settings.AZURE_OPENAI_API_KEY

# Step 2: Create Azure OpenAI model
azure_model = OpenAIChatModel(
    model_name=settings.AZURE_OPENAI_DEPLOYMENT,  # e.g., "gpt-4o"
    provider='azure'  # This is the key!
)

# Step 3: Create agent with the Azure model
agent = Agent(azure_model, system_prompt="Your system prompt here")
```

#### Key Discovery

The critical finding was that `OpenAIChatModel.__init__()` accepts a `provider` parameter with the following options:
```python
provider: Literal[
    'azure',  # ← This is what we needed!
    'deepseek',
    'cerebras',
    'fireworks',
    'github',
    'grok',
    'heroku',
    'moonshotai',
    'ollama',
    'openai',
    'openai-chat',
    'openrouter',
    'together',
    'vercel',
    'litellm',
    'nebius',
    'ovhcloud',
    'gateway'
]
```

## Architecture

### Service Layer

**File**: `backend/app/services/llm_provider.py`

```python
class LLMProvider(str, Enum):
    """Available LLM providers."""
    CLAUDE = "claude"
    AZURE_OPENAI = "azure_openai"

class LLMProviderService:
    @staticmethod
    def get_available_providers() -> list[LLMProvider]:
        """Detect configured providers based on env vars."""
        available = []
        if settings.ANTHROPIC_API_KEY:
            available.append(LLMProvider.CLAUDE)
        if settings.AZURE_OPENAI_API_KEY and settings.AZURE_OPENAI_ENDPOINT:
            available.append(LLMProvider.AZURE_OPENAI)
        return available

    @staticmethod
    def get_default_provider() -> Optional[LLMProvider]:
        """Azure OpenAI (DNP) has priority if configured."""
        available = LLMProviderService.get_available_providers()
        if LLMProvider.AZURE_OPENAI in available:
            return LLMProvider.AZURE_OPENAI
        if LLMProvider.CLAUDE in available:
            return LLMProvider.CLAUDE
        return None
```

### Agent Implementation

**File**: `backend/app/agents/population_agent.py`

```python
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIChatModel

class PopulationAgent:
    def __init__(self, model_name: str = "openai:gpt-4", provider: Optional[LLMProvider] = None):
        self.provider = provider

        if provider == LLMProvider.AZURE_OPENAI:
            # Set required environment variables for Azure
            import os
            os.environ["OPENAI_API_VERSION"] = settings.AZURE_OPENAI_API_VERSION
            os.environ["AZURE_OPENAI_ENDPOINT"] = settings.AZURE_OPENAI_ENDPOINT
            os.environ["AZURE_OPENAI_API_KEY"] = settings.AZURE_OPENAI_API_KEY

            # Create Azure OpenAI model
            azure_model = OpenAIChatModel(
                model_name=settings.AZURE_OPENAI_DEPLOYMENT,
                provider='azure'
            )

            # Create agent with Azure model
            self.agent = Agent(
                azure_model,
                output_type=SQLQuery,
                system_prompt="""..."""
            )
        else:
            # Default Claude or standard OpenAI
            self.agent = Agent(
                model_name,
                output_type=SQLQuery,
                system_prompt="""..."""
            )
```

### API Endpoint

**File**: `backend/app/api/v1/endpoints/chat.py`

```python
# Provider caching for performance
_agents_cache = {}

def get_agents(provider: LLMProvider = None):
    """Initialize agents for a specific provider with caching."""
    if provider is None:
        provider = LLMProviderService.get_default_provider()

    # Validate provider
    is_valid, error_msg = LLMProviderService.validate_provider(provider)
    if not is_valid:
        raise HTTPException(status_code=503, detail=error_msg)

    # Check cache
    if provider not in _agents_cache:
        model_name = LLMProviderService.get_model_name(provider)
        _agents_cache[provider] = (
            PopulationAgent(model_name=model_name, provider=provider),
            VisualizationAgent(model_name=model_name, provider=provider)
        )

    return _agents_cache[provider]

@router.get("/providers")
async def get_available_providers():
    """Get list of available LLM providers."""
    available = LLMProviderService.get_available_providers()
    default = LLMProviderService.get_default_provider()
    return {
        "available": [p.value for p in available],
        "default": default.value if default else None
    }

@router.post("/query")
async def process_query(query: ChatQuery, db: Session = Depends(get_session)):
    """Process query with selected provider."""
    provider = LLMProvider(query.provider) if query.provider else None
    population_agent, viz_agent = get_agents(provider)
    # ... rest of query processing
```

### Frontend Integration

**File**: `frontend/src/app/chat/page.tsx`

```typescript
const [availableProviders, setAvailableProviders] = useState<string[]>([]);
const [selectedProvider, setSelectedProvider] = useState<string | null>(null);

// Load available providers on mount
useEffect(() => {
  const loadProviders = async () => {
    const response = await axios.get(`${API_URL}/chats/providers`);
    setAvailableProviders(response.data.available || []);
    setSelectedProvider(response.data.default);
  };
  loadProviders();
}, []);

// Send message with selected provider
const sendMessage = async (message: string) => {
  const response = await axios.post(`${API_URL}/chats/query`, {
    query: message,
    chat_id: chatId,
    provider: selectedProvider  // 'azure_openai' or 'claude'
  });
};
```

**File**: `frontend/src/components/ChatInterface.tsx`

```typescript
{availableProviders.length > 1 && onProviderChange && (
  <div className="flex items-center justify-between px-4 py-2 border-b">
    <span className="text-sm font-medium">Modelo LLM:</span>
    <select
      value={selectedProvider || ''}
      onChange={(e) => onProviderChange(e.target.value)}
      disabled={isLoading}
    >
      {availableProviders.map((provider) => (
        <option key={provider} value={provider}>
          {provider === 'azure_openai' ? 'Azure OpenAI (DNP)' : 'Claude (Anthropic)'}
        </option>
      ))}
    </select>
  </div>
)}
```

## Configuration

### Environment Variables Required

**For Claude:**
```bash
ANTHROPIC_API_KEY=sk-ant-api03-xxxxxxxxxxxxx
```

**For Azure OpenAI:**
```bash
AZURE_OPENAI_API_KEY=your-azure-api-key
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT=gpt-4o
AZURE_OPENAI_API_VERSION=2024-08-01-preview
```

**DNP Production Credentials:**
```bash
AZURE_OPENAI_API_KEY=<your-azure-openai-api-key>
AZURE_OPENAI_ENDPOINT=https://dnp-oai-obdies-dev.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT=gpt-4o
AZURE_OPENAI_API_VERSION=2024-08-01-preview
```

### Configuration in `backend/app/core/config.py`

```python
class Settings(BaseSettings):
    # AI / LLM
    ANTHROPIC_API_KEY: Optional[str] = None

    # Azure OpenAI (DNP)
    AZURE_OPENAI_API_KEY: Optional[str] = None
    AZURE_OPENAI_ENDPOINT: Optional[str] = None
    AZURE_OPENAI_DEPLOYMENT: str = "gpt-4o"
    AZURE_OPENAI_API_VERSION: str = "2024-08-01-preview"
```

## Testing

### Test Both Providers

```bash
# Test Azure OpenAI (DNP)
curl -X POST http://localhost:8000/api/v1/chats/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "¿Cuántos departamentos hay en Colombia?",
    "chat_id": 1,
    "provider": "azure_openai"
  }'

# Test Claude
curl -X POST http://localhost:8000/api/v1/chats/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "¿Cuál es la población de Bogotá?",
    "chat_id": 1,
    "provider": "claude"
  }'

# Check available providers
curl http://localhost:8000/api/v1/chats/providers
```

## Performance Optimizations

1. **Agent Caching**: Agents are created once per provider and cached in memory
2. **Lazy Initialization**: Agents only created when first used
3. **Environment Variable Caching**: Settings loaded once at startup

## Troubleshooting Guide

### Issue: "Unknown provider: azure-openai"
**Cause**: Using wrong model prefix
**Solution**: Use `OpenAIChatModel(model_name='gpt-4o', provider='azure')` instead of string prefix

### Issue: "Must provide api_version"
**Cause**: Missing `OPENAI_API_VERSION` environment variable
**Solution**: Set `os.environ["OPENAI_API_VERSION"] = settings.AZURE_OPENAI_API_VERSION`

### Issue: Provider dropdown not visible
**Cause**: CORS error or only one provider configured
**Solution**:
- Check BACKEND_CORS_ORIGINS includes frontend port
- Verify at least 2 providers are configured

### Issue: 401 Unauthorized with Azure
**Cause**: Invalid or missing API key
**Solution**: Verify `AZURE_OPENAI_API_KEY` is correct and not expired

## Key Learnings

1. **pydantic-ai has excellent Azure support** - Just need to know the right way to configure it
2. **Provider parameter is the key** - `OpenAIChatModel(provider='azure')` activates Azure mode
3. **Environment variables matter** - Must set `OPENAI_API_VERSION`, `AZURE_OPENAI_ENDPOINT`, and `AZURE_OPENAI_API_KEY`
4. **Caching is essential** - Creating agents is expensive, cache them per provider
5. **Frontend state management** - Provider selection needs to persist across the session

## Files Modified

### Backend
- `backend/app/core/config.py` - Added Azure OpenAI configuration
- `backend/app/services/llm_provider.py` - **NEW**: Provider management service
- `backend/app/agents/population_agent.py` - Azure OpenAI integration
- `backend/app/agents/visualization_agent.py` - Azure OpenAI integration
- `backend/app/api/v1/endpoints/chat.py` - Provider endpoints and caching
- `backend/app/schemas/chat.py` - Added provider field to ChatQuery

### Frontend
- `frontend/src/app/chat/page.tsx` - Provider state management
- `frontend/src/components/ChatInterface.tsx` - Provider selector UI

### Configuration
- `.env` - Added Azure OpenAI credentials
- `.env.example` - Added provider configuration template

## References

- [pydantic-ai Documentation](https://ai.pydantic.dev/)
- [pydantic-ai Azure Provider](https://github.com/pydantic/pydantic-ai/blob/main/pydantic_ai/providers/azure.py)
- [OpenAI Python SDK v2](https://github.com/openai/openai-python)
- [Azure OpenAI Service](https://azure.microsoft.com/en-us/products/ai-services/openai-service)

## Future Improvements

1. **Model Selection**: Allow users to choose specific models (e.g., GPT-4 vs GPT-3.5-turbo)
2. **Cost Tracking**: Log and display costs per provider per query
3. **Performance Metrics**: Compare response times and quality between providers
4. **Fallback Logic**: Automatically switch providers if one fails
5. **Provider-Specific Features**: Utilize unique capabilities of each provider (e.g., Claude's long context)

---

**Implementation Date**: January 2025
**pydantic-ai Version**: 1.14.0
**Status**: ✅ Production Ready

---

## Git Repositories

### Dual Remotes

This project uses two Git remotes:

| Remote | URL | Description |
|--------|-----|-------------|
| `origin` | `git@github.com:luisjavierbautista/dnp-osc-population-module.git` | GitHub (primary) |
| `dnp` | `https://tfs.dnp.gov.co/DNP-Interna/SVDU.OSC/_git/osc_poblacion` | DNP TFS (internal) |

### Pushing to Both Remotes

**Push to GitHub (origin):**
```bash
git push origin HEAD:main
```

**Push to DNP TFS (dnp):**
DNP TFS requires authentication via Basic Auth header with PAT token:
```bash
# Generate base64 auth token (replace YOUR_PAT with actual PAT)
echo -n ":YOUR_PAT" | base64

# Push using the base64 token
git -c http.extraHeader="Authorization: Basic BASE64_TOKEN" push dnp HEAD:main
```

**Example with actual command:**
```bash
git -c http.extraHeader="Authorization: Basic OmZsZXJ2N2R0ZWFtYWpxZ25va25kaDJqcG9tZGhqNWxkcnN6YjZwdHp6b2xmYWdldW9udGE=" push dnp HEAD:main
```

### Notes on DNP TFS Authentication

- PAT tokens work but require the `http.extraHeader` approach
- Standard URL-embedded credentials don't work reliably with this TFS instance
- TFS API version is 5.1 (not 6.0)
- Default branch on DNP TFS is `master`, but we push to `main`
