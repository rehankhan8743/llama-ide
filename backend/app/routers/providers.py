from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from ..providers.provider_factory import ProviderFactory
from ..providers.base import Provider, Message
import os
import json
import asyncio

router = APIRouter(prefix="/providers")

class ProviderConfig(BaseModel):
    name: str
    api_key: str = ""
    enabled: bool = False
    model: str = ""
    base_url: Optional[str] = None

class ChatRequest(BaseModel):
    messages: List[Dict[str, str]]
    model: str = "llama2"
    temperature: float = 0.7
    max_tokens: int = 1000

class ChatResponse(BaseModel):
    message: Dict[str, str]
    finish_reason: Optional[str] = None
    usage: Optional[Dict[str, Any]] = None

def get_provider_configs() -> Dict[str, ProviderConfig]:
    """Load provider configurations"""
    configs = {}

    # Ollama
    configs["ollama"] = ProviderConfig(
        name="ollama",
        enabled=True,
        model=os.getenv("OLLAMA_DEFAULT_MODEL", "llama2"),
        base_url=os.getenv("OLLAMA_HOST", "http://localhost:11434")
    )

    # OpenAI
    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key:
        configs["openai"] = ProviderConfig(
            name="openai",
            api_key=openai_key,
            enabled=True,
            model=os.getenv("OPENAI_DEFAULT_MODEL", "gpt-3.5-turbo")
        )

    # Anthropic
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    if anthropic_key:
        configs["anthropic"] = ProviderConfig(
            name="anthropic",
            api_key=anthropic_key,
            enabled=True,
            model=os.getenv("ANTHROPIC_DEFAULT_MODEL", "claude-2")
        )

    # Google
    google_key = os.getenv("GOOGLE_API_KEY")
    if google_key:
        configs["google"] = ProviderConfig(
            name="google",
            api_key=google_key,
            enabled=True,
            model=os.getenv("GOOGLE_DEFAULT_MODEL", "gemini-pro")
        )

    # Groq
    groq_key = os.getenv("GROQ_API_KEY")
    if groq_key:
        configs["groq"] = ProviderConfig(
            name="groq",
            api_key=groq_key,
            enabled=True,
            model=os.getenv("GROQ_DEFAULT_MODEL", "mixtral-8x7b-32768")
        )

    # Cohere
    cohere_key = os.getenv("COHERE_API_KEY")
    if cohere_key:
        configs["cohere"] = ProviderConfig(
            name="cohere",
            api_key=cohere_key,
            enabled=True,
            model=os.getenv("COHERE_DEFAULT_MODEL", "command")
        )

    # Hugging Face
    hf_key = os.getenv("HUGGINGFACE_API_KEY")
    if hf_key:
        configs["huggingface"] = ProviderConfig(
            name="huggingface",
            api_key=hf_key,
            enabled=True,
            model=os.getenv("HUGGINGFACE_DEFAULT_MODEL", "meta-llama/Llama-2-70b-chat-hf")
        )

    return configs

@router.get("/", response_model=Dict[str, ProviderConfig])
async def list_providers():
    """List all available providers and their configurations"""
    return get_provider_configs()

@router.get("/available")
async def get_available_providers():
    """Get list of available provider types"""
    return ProviderFactory.get_available_providers()

@router.post("/{provider_name}/chat/completion", response_model=ChatResponse)
async def chat_completion(provider_name: str, request: ChatRequest):
    """Chat completion endpoint for specific provider"""
    try:
        configs = get_provider_configs()

        if provider_name not in configs:
            raise HTTPException(status_code=400, detail=f"Provider {provider_name} not configured")

        config = configs[provider_name]
        if not config.enabled:
            raise HTTPException(status_code=400, detail=f"Provider {provider_name} not enabled")

        provider_kwargs = {}
        if config.api_key:
            provider_kwargs["api_key"] = config.api_key
        if config.base_url:
            provider_kwargs["base_url"] = config.base_url

        provider = ProviderFactory.create_provider(provider_name, **provider_kwargs)
        if not provider:
            raise HTTPException(status_code=500, detail=f"Failed to create provider {provider_name}")

        messages = [Message(role=msg["role"], content=msg["content"]) for msg in request.messages]

        result = await provider.chat_completion(
            messages=messages,
            model=request.model or config.model,
            temperature=request.temperature,
            max_tokens=request.max_tokens
        )

        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])

        return ChatResponse(
            message=result["message"],
            finish_reason=result.get("finish_reason"),
            usage=result.get("usage")
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{provider_name}/chat/stream")
async def chat_stream(provider_name: str, request: ChatRequest):
    """Streaming chat completion endpoint for specific provider"""
    async def generate():
        try:
            configs = get_provider_configs()

            if provider_name not in configs:
                yield f"data: {json.dumps({'error': f'Provider {provider_name} not configured'})}\n\n"
                return

            config = configs[provider_name]
            if not config.enabled:
                yield f"data: {json.dumps({'error': f'Provider {provider_name} not enabled'})}\n\n"
                return

            provider_kwargs = {}
            if config.api_key:
                provider_kwargs["api_key"] = config.api_key
            if config.base_url:
                provider_kwargs["base_url"] = config.base_url

            provider = ProviderFactory.create_provider(provider_name, **provider_kwargs)
            if not provider:
                yield f"data: {json.dumps({'error': f'Failed to create provider {provider_name}'})}\n\n"
                return

            messages = [Message(role=msg["role"], content=msg["content"]) for msg in request.messages]

            async for chunk in provider.stream_chat(
                messages=messages,
                model=request.model or config.model,
                temperature=request.temperature,
                max_tokens=request.max_tokens
            ):
                yield f"data: {chunk}\n\n"

            yield "data: [DONE]\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")
