from typing import List, Dict, Any, AsyncGenerator, Optional
import httpx
import json
import os
from .base import Provider, Message


class HuggingFaceProvider(Provider):
    """Hugging Face Inference API provider"""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("HUGGINGFACE_API_KEY")
        self.base_url = "https://api-inference.huggingface.co/models"
        self.client = httpx.AsyncClient(timeout=60.0)
        self.default_model = "meta-llama/Llama-2-70b-chat-hf"

    async def chat_completion(
        self,
        messages: List[Message],
        model: str = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate a chat completion using Hugging Face"""
        try:
            if not self.api_key:
                raise ValueError("Hugging Face API key not configured")

            model_id = model or self.default_model

            # Format messages for the model
            prompt = self._format_messages(messages)

            payload = {
                "inputs": prompt,
                "parameters": {
                    "temperature": kwargs.get("temperature", 0.7),
                    "max_new_tokens": kwargs.get("max_tokens", 1000),
                    "return_full_text": False,
                    "do_sample": True,
                },
            }

            response = await self.client.post(
                f"{self.base_url}/{model_id}",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json=payload,
            )

            if response.status_code == 503:
                # Model is loading
                return {
                    "message": {
                        "role": "assistant",
                        "content": "Model is currently loading. Please try again in a moment.",
                    },
                    "finish_reason": "error",
                }

            response.raise_for_status()
            data = response.json()

            # Handle different response formats
            if isinstance(data, list) and len(data) > 0:
                content = data[0].get("generated_text", "")
            elif isinstance(data, dict):
                content = data.get("generated_text", "")
            else:
                content = str(data)

            return {
                "message": {
                    "role": "assistant",
                    "content": content,
                },
                "finish_reason": "stop",
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
        model: str = None,
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """Stream chat completions from Hugging Face"""
        # Hugging Face Inference API doesn't support streaming
        # Return the full response as a single chunk
        try:
            result = await self.chat_completion(messages, model, **kwargs)
            content = result.get("message", {}).get("content", "")
            if content:
                yield json.dumps({"content": content})
            yield json.dumps({"done": True})
        except Exception as e:
            yield json.dumps({"error": str(e)})

    def _format_messages(self, messages: List[Message]) -> str:
        """Format messages into a prompt string"""
        # Format for Llama-2-chat style models
        formatted = ""
        system_message = None

        for msg in messages:
            if msg.role == "system":
                system_message = msg.content
            elif msg.role == "user":
                if system_message:
                    formatted += f"[INST] <<SYS>>\n{system_message}\n<</SYS>>\n\n{msg.content} [/INST] "
                    system_message = None
                else:
                    formatted += f"[INST] {msg.content} [/INST] "
            elif msg.role == "assistant":
                formatted += f"{msg.content} "

        return formatted.strip()

    async def list_models(self) -> List[Dict[str, str]]:
        """List recommended Hugging Face models"""
        return [
            {"id": "meta-llama/Llama-2-70b-chat-hf", "name": "Llama 2 70B Chat"},
            {"id": "meta-llama/Llama-2-13b-chat-hf", "name": "Llama 2 13B Chat"},
            {"id": "meta-llama/Llama-2-7b-chat-hf", "name": "Llama 2 7B Chat"},
            {"id": "mistralai/Mistral-7B-Instruct-v0.2", "name": "Mistral 7B Instruct"},
            {"id": "google/gemma-7b-it", "name": "Gemma 7B IT"},
            {"id": "tiiuae/falcon-7b-instruct", "name": "Falcon 7B Instruct"},
            {"id": "HuggingFaceH4/zephyr-7b-beta", "name": "Zephyr 7B Beta"},
        ]

    async def text_generation(
        self,
        prompt: str,
        model: str = None,
        **kwargs
    ) -> str:
        """Text generation endpoint"""
        try:
            if not self.api_key:
                raise ValueError("Hugging Face API key not configured")

            model_id = model or self.default_model

            payload = {
                "inputs": prompt,
                "parameters": {
                    "temperature": kwargs.get("temperature", 0.7),
                    "max_new_tokens": kwargs.get("max_tokens", 1000),
                    "return_full_text": False,
                },
            }

            response = await self.client.post(
                f"{self.base_url}/{model_id}",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json=payload,
            )

            response.raise_for_status()
            data = response.json()

            if isinstance(data, list) and len(data) > 0:
                return data[0].get("generated_text", "")
            return str(data)

        except Exception as e:
            return f"Error: {str(e)}"

    async def text_embedding(
        self,
        text: str,
        model: str = "sentence-transformers/all-MiniLM-L6-v2"
    ) -> List[float]:
        """Generate text embeddings"""
        try:
            if not self.api_key:
                raise ValueError("Hugging Face API key not configured")

            payload = {"inputs": text}

            response = await self.client.post(
                f"{self.base_url}/{model}",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json=payload,
            )

            response.raise_for_status()
            data = response.json()

            if isinstance(data, list):
                return data
            return []

        except Exception as e:
            return []

    async def is_model_available(self, model: str) -> bool:
        """Check if a model is available"""
        try:
            response = await self.client.get(
                f"{self.base_url}/{model}",
                headers={"Authorization": f"Bearer {self.api_key}"},
            )
            return response.status_code == 200
        except:
            return False
