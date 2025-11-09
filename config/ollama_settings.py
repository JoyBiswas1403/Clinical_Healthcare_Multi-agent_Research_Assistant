"""Settings for using Ollama as free LLM alternative."""
from openai import OpenAI

# Ollama provides OpenAI-compatible API
def get_ollama_client():
    """Get Ollama client configured for local models."""
    return OpenAI(
        base_url="http://localhost:11434/v1",
        api_key="ollama"  # Ollama doesn't need real API key
    )

# Recommended free models:
# - llama3.2:3b (fast, good for general use)
# - qwen2.5:7b (better quality, slower)
# - mistral:7b (balanced)

OLLAMA_MODEL = "llama3.2:3b"
