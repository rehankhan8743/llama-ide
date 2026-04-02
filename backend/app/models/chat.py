from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class ChatMessage(BaseModel):
    role: str
    content: str
    timestamp: datetime = datetime.now()

class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    model: str = "llama2"
    temperature: float = 0.7
    max_tokens: int = 1000

class ChatResponse(BaseModel):
    message: ChatMessage
    finish_reason: Optional[str] = None
