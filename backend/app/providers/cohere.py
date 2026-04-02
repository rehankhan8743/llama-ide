from typing import List, Dict, Any, AsyncGenerator, Optional
import httpx
import json
import os
from .base import Provider, Message


class CohereProvider(Provider):
    """Cohere API provider implementation"""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("COHERE_API_KEY")
        self.base_url = "https://api.cohere.ai/v1"
        self.client = httpx.AsyncClient(timeout=60.0)

    async def chat_completion(
        self,
        messages: List[Message],
        model: str = "command",
        **kwargs
    ) -> Dict[str, Any]:
        """Generate a chat completion using Cohere"""
        try:
            if not self.api_key:
                raise ValueError("Cohere API key not configured")

            # Convert messages to Cohere format
            # Cohere uses 'message' for the current prompt and 'chat_history' for context
            chat_history = []
            for i, msg in enumerate(messages[:-1]):
                if msg.role == "user":
                    chat_history.append({"role": "USER", "message": msg.content})
                elif msg.role == "assistant":
                    chat_history.append({"role": "CHATBOT", "message": msg.content})

            current_message = messages[-1].content if messages else ""

            payload = {
                "message": current_message,
                "model": model,
                "chat_history": chat_history,
                "temperature": kwargs.get("temperature", 0.7),
                "max_tokens": kwargs.get("max_tokens", 1000),
                "stream": False,
            }

            response = await self.client.post(
                f"{self.base_url}/chat",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json=payload,
            )

            response.raise_for_status()
            data = response.json()

            return {
                "message": {
                    "role": "assistant",
                    "content": data.get("text", ""),
                },
                "finish_reason": "stop",
                "usage": {
                    "prompt_tokens": data.get("token_count", {}).get("prompt_tokens", 0),
                    "completion_tokens": data.get("token_count", {}).get("response_tokens", 0),
                },
            }

        except Exception as e:
            return {
                "error": str(e),
                "message": {
                    "role": "assistant",
                    "content": f"Error: {str(e)}",
                },
            }

    async def stream_chat(
        self,
        messages: List[Message],
        model: str = "command",
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """Stream chat completions from Cohere"""
        try:
            if not self.api_key:
                raise ValueError("Cohere API key not configured")

            # Convert messages to Cohere format
            chat_history = []
            for i, msg in enumerate(messages[:-1]):
                if msg.role == "user":
                    chat_history.append({"role": "USER", "message": msg.content})
                elif msg.role == "assistant":
                    chat_history.append({"role": "CHATBOT", "message": msg.content})

            current_message = messages[-1].content if messages else ""

            payload = {
                "message": current_message,
                "model": model,
                "chat_history": chat_history,
                "temperature": kwargs.get("temperature", 0.7),
                "max_tokens": kwargs.get("max_tokens", 1000),
                "stream": True,
            }

            async with self.client.stream(
                "POST",
                f"{self.base_url}/chat",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                    "Accept": "text/event-stream",
                },
                json=payload,
            ) as response:
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data = line[6:]
                        if data == "[DONE]":
                            yield json.dumps({"done": True})
                            break
                        try:
                            parsed = json.loads(data)
                            if "text" in parsed:
                                yield json.dumps({"content": parsed["text"]})
                        except:
                            pass

        except Exception as e:
            yield json.dumps({"error": str(e)})

    async def list_models(self) -> List[Dict[str, str]]:
        """List available Cohere models"""
        return [
            {"id": "command", "name": "Command"},
            {"id": "command-r", "name": "Command R"},
            {"id": "command-r-plus", "name": "Command R Plus"},
            {"id": "command-nightly", "name": "Command Nightly"},
        ]

    async def embed(self, texts: List[str], model: str = "embed-english-v3.0") -> List[List[float]]:
        """Generate embeddings for texts"""
        try:
            if not self.api_key:
                raise ValueError("Cohere API key not configured")

            payload = {
                "texts": texts,
                "model": model,
                "input_type": "search_document",
            }

            response = await self.client.post(
                f"{self.base_url}/embed",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json=payload,
            )

            response.raise_for_status()
            data = response.json()
            return data.get("embeddings", [])

        except Exception as e:
            return []


# Import Optional for type hints
from typing import Optional
