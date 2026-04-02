from typing import List, Dict, Any, AsyncGenerator
import httpx
import json
from .base import Provider, Message

class GoogleProvider(Provider):
    def __init__(self, api_key: str, base_url: str = "https://generativelanguage.googleapis.com/v1beta"):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.client = httpx.AsyncClient(
            timeout=300.0,
            params={"key": api_key}
        )

    async def chat_completion(self, messages: List[Message], model: str = "gemini-pro", **kwargs) -> Dict[str, Any]:
        """Generate a chat completion using Google Gemini API"""
        try:
            # Convert messages to Google format
            contents = []
            for msg in messages:
                contents.append({
                    "role": "user" if msg.role == "user" else "model",
                    "parts": [{"text": msg.content}]
                })

            payload = {
                "contents": contents,
                **kwargs
            }

            response = await self.client.post(
                f"{self.base_url}/models/{model}:generateContent",
                json=payload
            )

            response.raise_for_status()
            data = response.json()

            if "candidates" in data and len(data["candidates"]) > 0:
                candidate = data["candidates"][0]
                content = ""
                if "content" in candidate and "parts" in candidate["content"] and len(candidate["content"]["parts"]) > 0:
                    content = candidate["content"]["parts"][0]["text"]

                return {
                    "message": {
                        "role": "assistant",
                        "content": content
                    },
                    "finish_reason": candidate.get("finishReason", "stop"),
                    "usage": data.get("usageMetadata", {})
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

    async def stream_chat(self, messages: List[Message], model: str = "gemini-pro", **kwargs) -> AsyncGenerator[str, None]:
        """Stream chat completions from Google Gemini API"""
        try:
            contents = []
            for msg in messages:
                contents.append({
                    "role": "user" if msg.role == "user" else "model",
                    "parts": [{"text": msg.content}]
                })

            payload = {
                "contents": contents,
                "generationConfig": {
                    "candidateCount": 1,
                    **kwargs
                }
            }

            async with self.client.stream(
                "POST",
                f"{self.base_url}/models/{model}:streamGenerateContent",
                json=payload
            ) as response:
                response.raise_for_status()
                async for chunk in response.aiter_text():
                    if chunk.strip():
                        yield chunk
        except Exception as e:
            yield json.dumps({"error": str(e)}) + "\n"
