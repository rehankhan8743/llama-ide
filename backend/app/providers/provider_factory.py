from typing import Dict, Optional
from .base import Provider
from .ollama import OllamaProvider
from .openai import OpenAIProvider
from .anthropic import AnthropicProvider
from .google import GoogleProvider
from .groq import GroqProvider
from .cohere import CohereProvider
from .huggingface import HuggingFaceProvider
import os

class ProviderFactory:
    """Factory for creating provider instances"""

    @staticmethod
    def create_provider(provider_name: str, **kwargs) -> Optional[Provider]:
        """Create a provider instance based on name and configuration"""
        try:
            if provider_name == "ollama":
                host = kwargs.get("host", os.getenv("OLLAMA_HOST", "http://localhost:11434"))
                return OllamaProvider(host=host)

            elif provider_name == "openai":
                api_key = kwargs.get("api_key", os.getenv("OPENAI_API_KEY", ""))
                if not api_key:
                    raise ValueError("OpenAI API key is required")
                base_url = kwargs.get("base_url", "https://api.openai.com/v1")
                return OpenAIProvider(api_key=api_key, base_url=base_url)

            elif provider_name == "anthropic":
                api_key = kwargs.get("api_key", os.getenv("ANTHROPIC_API_KEY", ""))
                if not api_key:
                    raise ValueError("Anthropic API key is required")
                base_url = kwargs.get("base_url", "https://api.anthropic.com/v1")
                return AnthropicProvider(api_key=api_key, base_url=base_url)

            elif provider_name == "google":
                api_key = kwargs.get("api_key", os.getenv("GOOGLE_API_KEY", ""))
                if not api_key:
                    raise ValueError("Google API key is required")
                base_url = kwargs.get("base_url", "https://generativelanguage.googleapis.com/v1beta")
                return GoogleProvider(api_key=api_key, base_url=base_url)

            elif provider_name == "groq":
                api_key = kwargs.get("api_key", os.getenv("GROQ_API_KEY", ""))
                if not api_key:
                    raise ValueError("Groq API key is required")
                base_url = kwargs.get("base_url", "https://api.groq.com/openai/v1")
                return GroqProvider(api_key=api_key, base_url=base_url)

            elif provider_name == "cohere":
                api_key = kwargs.get("api_key", os.getenv("COHERE_API_KEY", ""))
                if not api_key:
                    raise ValueError("Cohere API key is required")
                return CohereProvider(api_key=api_key)

            elif provider_name == "huggingface":
                api_key = kwargs.get("api_key", os.getenv("HUGGINGFACE_API_KEY", ""))
                if not api_key:
                    raise ValueError("Hugging Face API key is required")
                return HuggingFaceProvider(api_key=api_key)

            else:
                raise ValueError(f"Unsupported provider: {provider_name}")

        except Exception as e:
            print(f"Error creating provider {provider_name}: {e}")
            return None

    @staticmethod
    def get_available_providers() -> Dict[str, str]:
        """Get list of available providers"""
        return {
            "ollama": "Ollama (Local)",
            "openai": "OpenAI",
            "anthropic": "Anthropic",
            "google": "Google Gemini",
            "groq": "Groq",
            "cohere": "Cohere",
            "huggingface": "Hugging Face"
        }
