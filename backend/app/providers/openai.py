from typing import List, Dict, Any, AsyncGenerator
import httpx
import json
from .base import Provider, Message

class OpenAIProvider(Provider):
    def __init__(self, api_key: str, base_url: str = "https://api.openai.com/v1"):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.client = httpx.AsyncClient(
            timeout=300.0,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
        )

    async def chat_completion(self, messages: List[Message], model: str = "gpt-3.5-turbo", **kwargs) -> Dict[str, Any]:
        """Generate a chat completion using OpenAI API"""
        try:
            payload = {
                "model": model,
                "messages": [{"role": m.role, "content": m.content} for m in messages],
                **kwargs
            }

            response = await self.client.post(
                f"{self.base_url}/chat/completions",
                json=payload
            )

            response.raise_for_status()
            data = response.json()

            return {
                "message": {
                    "role": "assistant",
                    "content": data["choices"][0]["message"]["content"]
                },
                "finish_reason": data["choices"][0]["finish_reason"],
                "usage": data.get("usage", {})
            }
        except Exception as e:
            return {
                "error": str(e),
                "message": {"role": "assistant", "content": f"Error: {str(e)}"}
            }

    async def stream_chat(self, messages: List[Message], model: str = "gpt-3.5-turbo", **kwargs) -> AsyncGenerator[str, None]:
        """Stream chat completions from OpenAI API"""
        try:
            payload = {
                "model": model,
                "messages": [{"role": m.role, "content": m.content} for m in messages],
                "stream": True,
                **kwargs
            }

            async with self.client.stream(
                "POST",
                f"{self.base_url}/chat/completions",
                json=payload
            ) as response:
                response.raise_for_status()
                async for chunk in response.aiter_text():
                    if chunk.strip():
                        yield chunk
        except Exception as e:
            yield json.dumps({"error": str(e)}) + "\n"
