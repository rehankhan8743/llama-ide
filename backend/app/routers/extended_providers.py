from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import os
from ..providers.extended_providers import MultiCloudProvider
from ..providers.provider_factory import ProviderFactory

router = APIRouter(prefix="/extended-providers")

# Initialize multi-cloud provider
multi_cloud = MultiCloudProvider()

class ProviderConfig(BaseModel):
    name: str
    api_key: str
    enabled: bool = True
    model: str = "default"
    base_url: Optional[str] = None

class RouteRequest(BaseModel):
    task: str
    requirements: Dict[str, Any]
    messages: List[Dict[str, str]]

class CompareRequest(BaseModel):
    prompts: List[str]
    providers: Optional[List[str]] = None

class ProviderResponse(BaseModel):
    message: Dict[str, str]
    finish_reason: Optional[str] = None
    usage: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

# Load provider configurations from environment
def load_provider_configs():
    """Load provider configurations from environment variables"""
    configs = {}

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
            model=os.getenv("HUGGINGFACE_DEFAULT_MODEL", "microsoft/DialoGPT-large")
        )

    return configs

# Initialize providers
provider_configs = load_provider_configs()
for name, config in provider_configs.items():
    if config.enabled:
        try:
            provider = ProviderFactory.create_provider(name, api_key=config.api_key, base_url=config.base_url)
            if provider:
                multi_cloud.add_provider(name, provider)
                multi_cloud.configure_provider(name, config.dict())
        except Exception as e:
            print(f"Error initializing provider {name}: {e}")

@router.post("/route", response_model=ProviderResponse)
async def route_request(request: RouteRequest):
    """Route request to the best provider"""
    try:
        from ..providers.base import Message
        messages = [Message(**msg) for msg in request.messages]

        result = await multi_cloud.route_request(
            request.task,
            request.requirements,
            messages
        )

        return ProviderResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/compare", response_model=Dict[str, Dict[str, ProviderResponse]])
async def compare_providers(request: CompareRequest):
    """Compare outputs from multiple providers"""
    try:
        results = await multi_cloud.compare_results(
            request.prompts,
            request.providers
        )

        # Convert to response model
        formatted_results = {}
        for prompt, provider_results in results.items():
            formatted_results[prompt] = {}
            for provider_name, result in provider_results.items():
                formatted_results[prompt][provider_name] = ProviderResponse(**result)

        return formatted_results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/available")
async def get_available_providers():
    """Get list of available extended providers"""
    try:
        return {
            "providers": list(multi_cloud.providers.keys()),
            "configs": {name: config for name, config in provider_configs.items() if config.enabled}
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/configure/{provider_name}")
async def configure_provider(provider_name: str, config: ProviderConfig):
    """Configure a provider"""
    try:
        # Update configuration
        provider_configs[provider_name] = config

        # If enabling, initialize provider
        if config.enabled:
            provider = ProviderFactory.create_provider(
                provider_name,
                api_key=config.api_key,
                base_url=config.base_url
            )
            if provider:
                multi_cloud.add_provider(provider_name, provider)
                multi_cloud.configure_provider(provider_name, config.dict())
            else:
                raise HTTPException(status_code=500, detail=f"Failed to initialize provider {provider_name}")

        return {"message": f"Provider {provider_name} configured successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/providers/{provider_name}")
async def remove_provider(provider_name: str):
    """Remove a provider"""
    try:
        if provider_name in multi_cloud.providers:
            del multi_cloud.providers[provider_name]
        if provider_name in provider_configs:
            del provider_configs[provider_name]
        return {"message": f"Provider {provider_name} removed successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/models/{provider_name}")
async def get_provider_models(provider_name: str):
    """Get available models for a provider"""
    try:
        # Common models for each provider
        model_lists = {
            "cohere": [
                "command", "command-light", "command-nightly"
            ],
            "huggingface": [
                "microsoft/DialoGPT-large",
                "facebook/blenderbot-400M-distill",
                "google/flan-t5-base"
            ]
        }

        return {"models": model_lists.get(provider_name, [])}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/benchmark")
async def benchmark_providers(prompts: List[str]):
    """Benchmark providers with a set of prompts"""
    try:
        import time

        benchmark_results = {}
        for provider_name, provider in multi_cloud.providers.items():
            benchmark_results[provider_name] = {
                "responses": [],
                "avg_response_time": 0,
                "total_time": 0
            }

            total_time = 0
            responses = []

            from ..providers.base import Message
            for prompt in prompts:
                start_time = time.time()
                try:
                    message = Message(role="user", content=prompt)
                    result = await provider.chat_completion([message])
                    response_time = time.time() - start_time
                    total_time += response_time
                    responses.append({
                        "prompt": prompt,
                        "response": result,
                        "time": response_time
                    })
                except Exception as e:
                    response_time = time.time() - start_time
                    total_time += response_time
                    responses.append({
                        "prompt": prompt,
                        "error": str(e),
                        "time": response_time
                    })

            benchmark_results[provider_name] = {
                "responses": responses,
                "avg_response_time": total_time / len(prompts) if prompts else 0,
                "total_time": total_time
            }

        return benchmark_results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
