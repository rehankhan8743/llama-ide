from typing import List, Dict, Any, AsyncGenerator
import httpx
import json
from .base import Provider, Message

class OllamaProvider(Provider):
    def __init__(self, host: str = "http://localhost:11434"):
        self.host = host.rstrip("/")
        self.client = httpx.AsyncClient(timeout=30.0)

    async def chat_completion(self, messages: List[Message], model: str = "llama2", **kwargs) -> Dict[str, Any]:
        """Generate a chat completion using Ollama"""
        try:
            payload = {
                "model": model,
                "messages": [{"role": m.role, "content": m.content} for m in messages],
                **kwargs
            }

            response = await self.client.post(
                f"{self.host}/api/chat",
                json=payload
            )

            response.raise_for_status()
            data = response.json()

            return {
                "message": {
                    "role": "assistant",
                    "content": data.get("message", {}).get("content", "")
                },
                "finish_reason": data.get("done_reason", "stop")
            }
        except Exception as e:
            return {
                "error": str(e),
                "message": {"role": "assistant", "content": f"Error: {str(e)}"}
            }

    async def stream_chat(self, messages: List[Message], model: str = "llama2", **kwargs) -> AsyncGenerator[str, None]:
        """Stream chat completions from Ollama"""
        try:
            payload = {
                "model": model,
                "messages": [{"role": m.role, "content": m.content} for m in messages],
                "stream": True,
                **kwargs
            }

            async with self.client.stream(
                "POST",
                f"{self.host}/api/chat",
                json=payload
            ) as response:
                async for chunk in response.aiter_text():
                    if chunk.strip():
                        yield chunk
        except Exception as e:
            yield json.dumps({"error": str(e)})
