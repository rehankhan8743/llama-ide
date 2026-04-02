from abc import ABC, abstractmethod
from typing import List, Dict, Any, AsyncGenerator
from pydantic import BaseModel

class Message(BaseModel):
    role: str
    content: str

class Provider(ABC):
    @abstractmethod
    async def chat_completion(self, messages: List[Message], **kwargs) -> Dict[str, Any]:
        """Generate a chat completion"""
        pass

    @abstractmethod
    async def stream_chat(self, messages: List[Message], **kwargs) -> AsyncGenerator[str, None]:
        """Stream chat completions"""
        pass
