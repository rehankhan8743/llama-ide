from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import os
import json
from pathlib import Path

router = APIRouter()

# Settings file path
SETTINGS_FILE = Path("./settings.json")

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

class SettingsUpdate(BaseModel):
    theme: Optional[str] = None
    default_model: Optional[str] = None
    ollama_host: Optional[str] = None
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    auto_save: Optional[bool] = None
    word_wrap: Optional[bool] = None
    font_size: Optional[int] = None

# Default settings
DEFAULT_SETTINGS = Settings()

def load_settings() -> Settings:
    """Load settings from file or return defaults"""
    if SETTINGS_FILE.exists():
        try:
            with open(SETTINGS_FILE, "r") as f:
                data = json.load(f)
                return Settings(**data)
        except Exception as e:
            print(f"Error loading settings: {e}")
            return DEFAULT_SETTINGS
    return DEFAULT_SETTINGS

def save_settings(settings: Settings) -> None:
    """Save settings to file"""
    try:
        with open(SETTINGS_FILE, "w") as f:
            json.dump(settings.dict(), f, indent=2)
    except Exception as e:
        print(f"Error saving settings: {e}")
        raise HTTPException(status_code=500, detail="Failed to save settings")

# Load initial settings
current_settings = load_settings()

@router.get("/config", response_model=Settings)
async def get_config():
    """Get current configuration"""
    global current_settings
    current_settings = load_settings()
    return current_settings

@router.put("/config", response_model=Settings)
async def update_config(settings_update: SettingsUpdate):
    """Update configuration"""
    global current_settings

    # Apply updates
    update_data = settings_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(current_settings, field, value)

    # Save to file
    save_settings(current_settings)

    return current_settings

@router.get("/providers", response_model=Dict[str, ProviderConfig])
async def list_providers():
    """List available providers and their configurations"""
    # In a real implementation, this would load from a providers config file
    providers = {
        "ollama": ProviderConfig(
            name="ollama",
            enabled=True,
            model=current_settings.default_model
        ),
        "openai": ProviderConfig(
            name="openai",
            enabled=False,
            api_key=os.getenv("OPENAI_API_KEY", ""),
            model="gpt-3.5-turbo"
        ),
        "anthropic": ProviderConfig(
            name="anthropic",
            enabled=False,
            api_key=os.getenv("ANTHROPIC_API_KEY", ""),
            model="claude-2"
        ),
        "google": ProviderConfig(
            name="google",
            enabled=False,
            api_key=os.getenv("GOOGLE_API_KEY", ""),
            model="gemini-pro"
        )
    }
    return providers

@router.put("/providers/{provider_name}", response_model=ProviderConfig)
async def update_provider(provider_name: str, config: ProviderConfig):
    """Update provider configuration"""
    # In a real implementation, this would save to a providers config file
    # For now, we'll just return the updated config
    return config

@router.get("/themes", response_model=List[str])
async def list_themes():
    """List available themes"""
    return ["light", "dark", "blue", "green", "purple"]

@router.post("/reset")
async def reset_settings():
    """Reset settings to defaults"""
    global current_settings
    current_settings = DEFAULT_SETTINGS
    save_settings(current_settings)
    return {"message": "Settings reset to defaults"}

@router.get("/export")
async def export_settings():
    """Export current settings as JSON"""
    return current_settings.dict()

@router.post("/import")
async def import_settings(settings: Settings):
    """Import settings from JSON"""
    global current_settings
    current_settings = settings
    save_settings(current_settings)
    return {"message": "Settings imported successfully"}
