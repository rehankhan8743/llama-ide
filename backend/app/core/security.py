import os
from pathlib import Path

def validate_path(path: str, base_path: str = "./workspace") -> bool:
    """Validate that a path is within the allowed directory"""
    try:
        resolved_path = Path(path).resolve()
        base_resolved = Path(base_path).resolve()
        return str(resolved_path).startswith(str(base_resolved))
    except Exception:
        return False

def sanitize_input(input_str: str) -> str:
    """Basic input sanitization"""
    # Remove potentially dangerous characters
    dangerous_chars = [';', '&', '|', '`', '$(', '${']
    sanitized = input_str
    for char in dangerous_chars:
        sanitized = sanitized.replace(char, '')
    return sanitized
