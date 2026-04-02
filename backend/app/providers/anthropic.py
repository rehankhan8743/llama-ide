from typing import List, Dict, Any, AsyncGenerator
import httpx
import json
from .base import Provider, Message

class AnthropicProvider(Provider):
    def __init__(self, api_key: str, base_url: str = "https://api.anthropic.com/v1"):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.client = httpx.AsyncClient(
            timeout=300.0,
            headers={
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
                "Content-Type": "application/json"
            }
        )

    async def chat_completion(self, messages: List[Message], model: str = "claude-2", **kwargs) -> Dict[str, Any]:
        """Generate a chat completion using Anthropic API"""
        try:
            # Convert messages to Anthropic format
            prompt_parts = []
            for msg in messages:
                if msg.role == "user":
                    prompt_parts.append(f"\n\nHuman: {msg.content}")
                elif msg.role == "assistant":
                    prompt_parts.append(f"\n\nAssistant: {msg.content}")

            prompt = "".join(prompt_parts) + "\n\nAssistant:"

            payload = {
                "model": model,
                "prompt": prompt,
                "max_tokens_to_sample": kwargs.get("max_tokens", 1000),
                **{k: v for k, v in kwargs.items() if k not in ["max_tokens"]}
            }

            response = await self.client.post(
                f"{self.base_url}/completions",
                json=payload
            )

            response.raise_for_status()
            data = response.json()

            return {
                "message": {
                    "role": "assistant",
                    "content": data["completion"]
                },
                "finish_reason": "stop",
                "usage": {}
            }
        except Exception as e:
            return {
                "error": str(e),
                "message": {"role": "assistant", "content": f"Error: {str(e)}"}
            }

    async def stream_chat(self, messages: List[Message], model: str = "claude-2", **kwargs) -> AsyncGenerator[str, None]:
        """Stream chat completions from Anthropic API"""
        try:
            prompt_parts = []
            for msg in messages:
                if msg.role == "user":
                    prompt_parts.append(f"\n\nHuman: {msg.content}")
                elif msg.role == "assistant":
                    prompt_parts.append(f"\n\nAssistant: {msg.content}")

            prompt = "".join(prompt_parts) + "\n\nAssistant:"

            payload = {
                "model": model,
                "prompt": prompt,
                "max_tokens_to_sample": kwargs.get("max_tokens", 1000),
                "stream": True,
                **{k: v for k, v in kwargs.items() if k not in ["max_tokens"]}
            }

            async with self.client.stream(
                "POST",
                f"{self.base_url}/completions",
                json=payload
            ) as response:
                response.raise_for_status()
                async for chunk in response.aiter_text():
                    if chunk.strip():
                        yield chunk
        except Exception as e:
            yield json.dumps({"error": str(e)}) + "\n"
