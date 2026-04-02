from pydantic import BaseModel
from typing import Dict, Any

class Settings(BaseModel):
    theme: str = "dark"
    default_model: str = "llama2"
    ollama_host: str = "http://localhost:11434"
    temperature: float = 0.7
    max_tokens: int = 1000
    auto_save: bool = True
    word_wrap: bool = True
    font_size: int = 14

class ProviderConfig(BaseModel):
    name: str
    api_key: str = ""
    enabled: bool = False
    model: str = ""
    base_url: str = ""
