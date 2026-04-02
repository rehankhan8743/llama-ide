from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime

class ChatMessage(BaseModel):
    role: str
    content: str
    timestamp: datetime

class EditorFileState(BaseModel):
    filepath: str
    content: str
    cursor_position: Optional[Dict[str, int]] = None
    scroll_position: Optional[Dict[str, int]] = None
    language: str

class SessionState(BaseModel):
    id: str
    name: str
    created_at: datetime
    updated_at: datetime
    chat_history: List[ChatMessage]
    editor_files: List[EditorFileState]
    active_filepath: Optional[str] = None
    settings: Dict[str, Any] = {}
    git_branch: Optional[str] = None

class CreateSessionRequest(BaseModel):
    name: str
    template_session_id: Optional[str] = None

class UpdateSessionRequest(BaseModel):
    name: Optional[str] = None
    chat_history: Optional[List[ChatMessage]] = None
    editor_files: Optional[List[EditorFileState]] = None
    active_filepath: Optional[str] = None
    settings: Optional[Dict[str, Any]] = None
    git_branch: Optional[str] = None
