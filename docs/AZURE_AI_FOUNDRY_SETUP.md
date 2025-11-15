# Azure AI Foundry Configuration

## Overview

This project uses **Azure AI Foundry** (not Azure OpenAI Service) to enable multi-model support and access to various AI models beyond just OpenAI models.

## Key Differences: Azure AI Foundry vs Azure OpenAI Service

| Feature | Azure OpenAI Service | Azure AI Foundry |
|---------|---------------------|------------------|
| **Endpoint Format** | `https://<resource>.openai.azure.com/` | `https://<resource>.services.ai.azure.com/api/projects/<projectName>` |
| **Model Support** | OpenAI models only (GPT-4, GPT-3.5) | Multiple providers (OpenAI, Meta, Mistral, etc.) |
| **Deployment** | Fixed deployments | Flexible model selection |
| **SDK** | `openai` Python package | `openai` or `azure-ai-inference` packages |
| **Use Case** | OpenAI-specific applications | Multi-model experimentation |

## Current Configuration

### Endpoint Structure
```
https://wkm-aif.services.ai.azure.com/api/projects/firstProject
```

This endpoint provides access to your Azure AI Foundry project, which can host multiple models.

### Python SDK Compatibility

**Good News**: The `openai` Python SDK's `AsyncAzureOpenAI` client **works with Azure AI Foundry endpoints**!

You don't need to change SDKs. The current implementation using `AsyncAzureOpenAI` is correct:

```python
from openai import AsyncAzureOpenAI

client = AsyncAzureOpenAI(
    azure_endpoint="https://wkm-aif.services.ai.azure.com/api/projects/firstProject",
    api_key=AZURE_API_KEY,
    api_version="2024-08-01-preview",
)

response = await client.chat.completions.create(
    model="gpt-4",  # Or mistral-large, llama-3-70b, etc.
    messages=[...]
)
```

### Environment Variables

Required variables in your `.env` file:

```bash
# Azure AI Foundry Endpoint (includes project path)
AZURE_ENDPOINT=https://wkm-aif.services.ai.azure.com/api/projects/firstProject

# Azure AI Foundry API Key
AZURE_API_KEY=your-api-key-here

# Model deployment name (can be actual model name)
AZURE_DEPLOYMENT_NAME=gpt-4

# API version (use latest)
AZURE_API_VERSION=2024-08-01-preview
```

## Available Models in Azure AI Foundry

Azure AI Foundry supports multiple model providers:

### OpenAI Models
- `gpt-4` - Most capable GPT-4 model
- `gpt-4o` - Optimized GPT-4 for faster responses
- `gpt-35-turbo` - Faster, cheaper GPT-3.5

### Meta Models
- `llama-3-70b` - Large open-source model
- `llama-3-8b` - Smaller, faster Llama model

### Mistral Models
- `mistral-large` - Mistral's flagship model
- `mistral-small` - Faster Mistral variant

### Other Providers
- Cohere models
- Custom fine-tuned models

## How to Switch Models

To experiment with different models, simply change the `AZURE_DEPLOYMENT_NAME`:

```bash
# Use GPT-4
AZURE_DEPLOYMENT_NAME=gpt-4

# Switch to Mistral
AZURE_DEPLOYMENT_NAME=mistral-large

# Try Llama 3
AZURE_DEPLOYMENT_NAME=llama-3-70b
```

No code changes required! The same API calls work across all models.

## Code Implementation

### Backend API Route (`backend/src/api/routes/chat.py`)

The current implementation already supports Azure AI Foundry:

```python
async def get_openai_client() -> AsyncAzureOpenAI:
    """Create Azure AI Foundry client using OpenAI SDK."""
    client = AsyncAzureOpenAI(
        azure_endpoint=AZURE_ENDPOINT,  # Foundry endpoint
        api_key=AZURE_API_KEY,
        api_version=AZURE_API_VERSION,
    )
    return client
```

### Chat Service (`shared/chat_service.py`)

Tool calling and chat completions work identically:

```python
response = await client.chat.completions.create(
    model=AZURE_DEPLOYMENT_NAME,  # Specified in .env
    messages=messages,
    tools=TOOLS,  # Function calling supported
    tool_choice="auto",
)
```

## Function Calling / Tool Use

Azure AI Foundry supports OpenAI-style function calling for all compatible models:

- ✅ **GPT-4**: Full function calling support
- ✅ **GPT-3.5-turbo**: Full function calling support
- ⚠️ **Mistral Large**: Supports function calling with slight differences
- ❌ **Llama 3**: Limited/no native function calling

Our current tool definitions work seamlessly with GPT models in Foundry.

## Testing Your Setup

1. **Verify your `.env` file**:
   ```bash
   cat .env | grep AZURE_
   ```

2. **Check the endpoint format**:
   - Should include `/api/projects/projectName`
   - Must start with `https://`

3. **Test the API**:
   ```bash
   # Start backend
   PYTHONPATH=. backend/venv/bin/uvicorn backend.src.api.main:app --reload --port 8000

   # Test chat endpoint
   curl -X POST http://localhost:8000/api/chat \
     -H "Content-Type: application/json" \
     -d '{"message": "What is the current OEE?"}'
   ```

4. **Check logs**:
   - Backend should log: "Azure OpenAI client created successfully"
   - No errors about endpoint format or authentication

## Migration Notes

### What Changed
- ✅ Updated `.env.example` with Foundry endpoint format
- ✅ Added documentation clarifying Foundry vs OpenAI Service
- ✅ Confirmed OpenAI SDK compatibility with Foundry

### What Stayed the Same
- ✅ Python SDK (`openai` package) - no change needed
- ✅ Client initialization code - works as-is
- ✅ API calls and function calling - identical syntax
- ✅ All existing tests - should pass without modification

## Benefits of Azure AI Foundry

1. **Multi-Model Experimentation**: Switch between GPT-4, Mistral, Llama without code changes
2. **Cost Optimization**: Try cheaper models (GPT-3.5, Mistral Small) for simpler tasks
3. **Future-Proof**: Easy to adopt new models as they're added to Foundry
4. **Unified API**: Single endpoint for all models

## Troubleshooting

### Error: "Invalid endpoint format"
- **Fix**: Ensure endpoint includes `/api/projects/projectName`
- **Correct**: `https://wkm-aif.services.ai.azure.com/api/projects/firstProject`
- **Incorrect**: `https://wkm-aif.services.ai.azure.com/`

### Error: "Model not found"
- **Fix**: Check your model deployment name in Azure AI Foundry portal
- Ensure `AZURE_DEPLOYMENT_NAME` matches the deployed model

### Error: "Authentication failed"
- **Fix**: Regenerate API key from Azure AI Foundry portal
- Verify key is copied correctly (no extra spaces/newlines)

### Function calling not working
- **Fix**: Ensure you're using a GPT model (gpt-4, gpt-35-turbo)
- Some models (Llama 3) don't support OpenAI-style function calling

## References

- [Azure AI Foundry Documentation](https://learn.microsoft.com/en-us/azure/ai-foundry/)
- [OpenAI Python SDK](https://github.com/openai/openai-python)
- [Azure AI Foundry Chat Completions](https://learn.microsoft.com/en-us/azure/ai-foundry/foundry-models/how-to/use-chat-completions)
