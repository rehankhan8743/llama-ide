from typing import List, Dict, Any, AsyncGenerator
import httpx
import json
from .base import Provider, Message

class CohereProvider(Provider):
    def __init__(self, api_key: str, base_url: str = "https://api.cohere.ai/v1"):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.client = httpx.AsyncClient(
            timeout=300.0,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
        )

    async def chat_completion(self, messages: List[Message], model: str = "command", **kwargs) -> Dict[str, Any]:
        """Generate a chat completion using Cohere API"""
        try:
            # Convert messages to Cohere format
            chat_history = []
            prompt = ""

            for i, msg in enumerate(messages):
                if msg.role == "user":
                    if i == len(messages) - 1:  # Last message is the prompt
                        prompt = msg.content
                    else:
                        chat_history.append({"user_name": "User", "text": msg.content})
                elif msg.role == "assistant":
                    chat_history.append({"user_name": "Chatbot", "text": msg.content})

            payload = {
                "model": model,
                "chat_history": chat_history,
                "message": prompt,
                **kwargs
            }

            response = await self.client.post(
                f"{self.base_url}/chat",
                json=payload
            )

            response.raise_for_status()
            data = response.json()

            return {
                "message": {
                    "role": "assistant",
                    "content": data["text"]
                },
                "finish_reason": data.get("finish_reason", "complete"),
                "usage": data.get("meta", {}).get("tokens", {})
            }
        except Exception as e:
            return {
                "error": str(e),
                "message": {"role": "assistant", "content": f"Error: {str(e)}"}
            }

    async def stream_chat(self, messages: List[Message], model: str = "command", **kwargs) -> AsyncGenerator[str, None]:
        """Stream chat completions from Cohere API"""
        try:
            # Convert messages to Cohere format
            chat_history = []
            prompt = ""

            for i, msg in enumerate(messages):
                if msg.role == "user":
                    if i == len(messages) - 1:  # Last message is the prompt
                        prompt = msg.content
                    else:
                        chat_history.append({"user_name": "User", "text": msg.content})
                elif msg.role == "assistant":
                    chat_history.append({"user_name": "Chatbot", "text": msg.content})

            payload = {
                "model": model,
                "chat_history": chat_history,
                "message": prompt,
                "stream": True,
                **kwargs
            }

            async with self.client.stream(
                "POST",
                f"{self.base_url}/chat",
                json=payload
            ) as response:
                response.raise_for_status()
                async for chunk in response.aiter_text():
                    if chunk.strip():
                        yield chunk
        except Exception as e:
            yield json.dumps({"error": str(e)}) + "\n"

class HuggingFaceProvider(Provider):
    def __init__(self, api_key: str, base_url: str = "https://api-inference.huggingface.co"):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.client = httpx.AsyncClient(
            timeout=300.0,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
        )

    async def chat_completion(self, messages: List[Message], model: str = "microsoft/DialoGPT-large", **kwargs) -> Dict[str, Any]:
        """Generate a chat completion using Hugging Face API"""
        try:
            # Combine messages into a single prompt
            prompt = ""
            for msg in messages:
                if msg.role == "user":
                    prompt += f"User: {msg.content}\n"
                elif msg.role == "assistant":
                    prompt += f"Assistant: {msg.content}\n"

            payload = {
                "inputs": prompt,
                "parameters": {
                    "max_new_tokens": kwargs.get("max_tokens", 1000),
                    "temperature": kwargs.get("temperature", 0.7),
                    "top_p": kwargs.get("top_p", 0.9),
                    "repetition_penalty": 1.2
                }
            }

            response = await self.client.post(
                f"{self.base_url}/models/{model}",
                json=payload
            )

            response.raise_for_status()
            data = response.json()

            if isinstance(data, list) and len(data) > 0:
                generated_text = data[0].get("generated_text", "")
                # Extract only the assistant's response
                if "Assistant:" in generated_text:
                    response_text = generated_text.split("Assistant:")[-1].strip()
                else:
                    response_text = generated_text.strip()

                return {
                    "message": {
                        "role": "assistant",
                        "content": response_text
                    },
                    "finish_reason": "complete"
                }
            else:
                return {
                    "message": {"role": "assistant", "content": "No response generated"},
                    "finish_reason": "none"
                }
        except Exception as e:
            return {
                "error": str(e),
                "message": {"role": "assistant", "content": f"Error: {str(e)}"}
            }

    async def stream_chat(self, messages: List[Message], model: str = "microsoft/DialoGPT-large", **kwargs) -> AsyncGenerator[str, None]:
        """Stream chat completions from Hugging Face API"""
        # Hugging Face doesn't support streaming in the same way, so we'll simulate it
        try:
            result = await self.chat_completion(messages, model, **kwargs)
            if "error" not in result:
                content = result["message"]["content"]
                # Yield content in chunks
                chunk_size = 20
                for i in range(0, len(content), chunk_size):
                    chunk = content[i:i + chunk_size]
                    yield json.dumps({"token": {"text": chunk}}) + "\n"
            else:
                yield json.dumps(result) + "\n"
        except Exception as e:
            yield json.dumps({"error": str(e)}) + "\n"

class MultiCloudProvider:
    def __init__(self):
        self.providers = {}
        self.provider_configs = {}

    def add_provider(self, name: str, provider: Provider):
        """Add a provider to the multi-cloud system"""
        self.providers[name] = provider

    def configure_provider(self, name: str, config: Dict[str, Any]):
        """Configure a provider"""
        self.provider_configs[name] = config

    async def route_request(self, task: str, requirements: Dict[str, Any], messages: List[Message]) -> Dict[str, Any]:
        """Intelligently route requests to best provider"""
        # Simple routing logic based on task type
        if "code" in task.lower() or "programming" in task.lower():
            provider_name = "openai" if "openai" in self.providers else list(self.providers.keys())[0]
        elif "creative" in task.lower() or "writing" in task.lower():
            provider_name = "anthropic" if "anthropic" in self.providers else list(self.providers.keys())[0]
        elif "data" in task.lower() or "analysis" in task.lower():
            provider_name = "google" if "google" in self.providers else list(self.providers.keys())[0]
        else:
            # Default to first available provider
            provider_name = list(self.providers.keys())[0]

        if provider_name in self.providers:
            provider = self.providers[provider_name]
            model = requirements.get("model", "default")
            return await provider.chat_completion(messages, model=model, **requirements)
        else:
            return {"error": f"Provider {provider_name} not available"}

    async def compare_results(self, prompts: List[str], providers: List[str] = None) -> Dict[str, Any]:
        """Compare outputs from multiple providers"""
        if providers is None:
            providers = list(self.providers.keys())

        comparison_results = {}

        for prompt in prompts:
            comparison_results[prompt] = {}
            message = Message(role="user", content=prompt)

            for provider_name in providers:
                if provider_name in self.providers:
                    try:
                        result = await self.providers[provider_name].chat_completion([message])
                        comparison_results[prompt][provider_name] = result
                    except Exception as e:
                        comparison_results[prompt][provider_name] = {"error": str(e)}

        return comparison_results

# Initialize extended providers
extended_providers = {
    "cohere": CohereProvider,
    "huggingface": HuggingFaceProvider
}
