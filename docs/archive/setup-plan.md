# Azure AI Foundry Migration - Setup Plan

## Summary

This document describes the migration of factory-agent from OpenRouter to Azure AI Foundry.

### 📁 New Project Location
- Created: `/Users/willmacdonald/Documents/Code/azure/factory-agent/`
- This is a completely separate directory from your OpenRouter version

### 🔧 Files Modified (7 files)

1. **`src/config.py`** - Azure configuration
   - Replaced `OPENROUTER_API_KEY`, `BASE_URL`, `OPENROUTER_MODEL`
   - Added `AZURE_ENDPOINT`, `AZURE_API_KEY`, `AZURE_DEPLOYMENT_NAME`

2. **`src/main.py`** - Client initialization
   - Changed from `OpenAI` client to `AzureOpenAI` client
   - Updated imports to include `AzureOpenAI`
   - Updated two client initializations (chat and voice functions)
   - Changed model parameter from `MODEL` to `AZURE_DEPLOYMENT_NAME`
   - Updated error messages to reference Azure instead of OpenRouter

3. **`.env`** - Environment variables
   - Replaced OpenRouter variables with Azure variables
   - Kept `OPENAI_API_KEY` for voice interface (Whisper/TTS)

4. **`.env.example`** - Template file
   - Updated with Azure configuration instructions
   - Added helpful comments for getting Azure credentials

5. **`requirements.txt`** - Dependencies
   - Added comment noting OpenAI SDK includes Azure support
   - No package changes needed (openai>=1.51.0 supports Azure)

6. **`README.md`** - Documentation
   - Updated description to mention Azure AI Foundry
   - Updated tech stack section
   - Added detailed Azure setup instructions
   - Updated all references from OpenRouter/Claude to Azure AI

7. **`tests/test_config.py`** - Configuration tests
   - Updated to test Azure config variables instead of OpenRouter

### ✅ Files Unchanged (~900 lines)
These modules work identically with Azure:
- `src/data.py` - Data generation
- `src/metrics.py` - All 4 analysis tools
- `src/dashboard.py` - Streamlit dashboard
- `tests/test_main.py` - Mock-based tests

### 🔑 Next Steps

To use the Azure version, you'll need to:

1. **Get Azure credentials** from Azure Portal:
   - Navigate to your Azure OpenAI resource
   - Copy endpoint URL (e.g., `https://your-resource.openai.azure.com/`)
   - Copy API key from "Keys and Endpoint" section
   - Note your model deployment name

2. **Update the `.env` file**:
   ```bash
   cd /Users/willmacdonald/Documents/Code/azure/factory-agent
   # Edit .env with your Azure credentials
   ```

3. **Test the setup**:
   ```bash
   cd /Users/willmacdonald/Documents/Code/azure/factory-agent
   source venv/bin/activate  # or create new venv
   pip install -r requirements.txt
   python -m src.main setup
   python -m src.main chat
   ```

### 📊 Migration Stats
- **7 files modified** with ~50-100 lines changed
- **~900 lines unchanged** (all business logic)
- **Clean separation** - Original OpenRouter version untouched at `/Users/willmacdonald/Documents/Code/claude/factory-agent/`

### 🏗️ Architecture Benefits

The architecture made this migration straightforward because:
- LLM client is only used in one module (`main.py`)
- All business logic is decoupled in separate modules
- Tool definitions and execution logic are provider-agnostic
- Configuration is centralized in `config.py`

### 🔄 Key Technical Changes

**Client Initialization (Before)**:
```python
from openai import OpenAI
client = OpenAI(base_url=BASE_URL, api_key=API_KEY)
```

**Client Initialization (After)**:
```python
from openai import AzureOpenAI
client = AzureOpenAI(
    azure_endpoint=AZURE_ENDPOINT,
    api_key=AZURE_API_KEY,
    api_version="2024-08-01-preview"
)
```

**API Call (Before)**:
```python
response = client.chat.completions.create(
    model=MODEL,  # e.g., "anthropic/claude-3.5-sonnet"
    messages=messages,
    tools=TOOLS,
    tool_choice="auto"
)
```

**API Call (After)**:
```python
response = client.chat.completions.create(
    model=AZURE_DEPLOYMENT_NAME,  # e.g., "gpt-4"
    messages=messages,
    tools=TOOLS,
    tool_choice="auto"
)
```

### 📝 Important Notes

1. **Voice Interface**: Still uses OpenAI directly for Whisper (STT) and TTS. You'll need both:
   - Azure credentials for the chatbot functionality
   - OpenAI API key for voice features

2. **API Compatibility**: Azure OpenAI uses the same OpenAI SDK, so tool-calling format and message structure remain identical

3. **Model Deployment**: In Azure, you deploy specific models (like GPT-4) with custom names. Use your deployment name, not the model ID.

4. **API Version**: Using `2024-08-01-preview` for latest features. Update as needed for your Azure setup.

5. **Git History**: Removed from Azure version to keep it separate from the original OpenRouter repository.
