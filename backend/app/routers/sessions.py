from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import uuid
from datetime import datetime
from ..models.session import SessionState, ChatMessage, EditorFileState, CreateSessionRequest, UpdateSessionRequest
from ..services.session_store import SessionStore

router = APIRouter()

# Initialize session store
session_store = SessionStore("sessions.db")

class SessionSummary(BaseModel):
    id: str
    name: str
    created_at: datetime
    updated_at: datetime

@router.post("/", response_model=SessionState)
async def create_session(request: CreateSessionRequest):
    """Create a new session"""
    try:
        session_id = str(uuid.uuid4())
        now = datetime.now()

        # If template session provided, copy its state
        chat_history = []
        editor_files = []
        settings = {}
        git_branch = None
        active_filepath = None

        if request.template_session_id:
            template_session = session_store.get_session(request.template_session_id)
            if template_session:
                chat_history = template_session.chat_history
                editor_files = template_session.editor_files
                settings = template_session.settings
                git_branch = template_session.git_branch
                active_filepath = template_session.active_filepath

        session = SessionState(
            id=session_id,
            name=request.name,
            created_at=now,
            updated_at=now,
            chat_history=chat_history,
            editor_files=editor_files,
            active_filepath=active_filepath,
            settings=settings,
            git_branch=git_branch
        )

        if session_store.create_session(session):
            return session
        else:
            raise HTTPException(status_code=500, detail="Failed to create session")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{session_id}", response_model=SessionState)
async def get_session(session_id: str):
    """Get a session by ID"""
    try:
        session = session_store.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        return session
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{session_id}", response_model=SessionState)
async def update_session(session_id: str, request: UpdateSessionRequest):
    """Update a session"""
    try:
        # First get the existing session
        session = session_store.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        # Update fields if provided
        if request.name is not None:
            session.name = request.name
        if request.chat_history is not None:
            session.chat_history = request.chat_history
        if request.editor_files is not None:
            session.editor_files = request.editor_files
        if request.active_filepath is not None:
            session.active_filepath = request.active_filepath
        if request.settings is not None:
            session.settings = request.settings
        if request.git_branch is not None:
            session.git_branch = request.git_branch

        session.updated_at = datetime.now()

        if session_store.update_session(session):
            return session
        else:
            raise HTTPException(status_code=500, detail="Failed to update session")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{session_id}")
async def delete_session(session_id: str):
    """Delete a session"""
    try:
        if session_store.delete_session(session_id):
            return {"message": "Session deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="Session not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=List[SessionSummary])
async def list_sessions():
    """List all sessions"""
    try:
        sessions = session_store.list_sessions()
        return sessions
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{session_id}/clone", response_model=SessionState)
async def clone_session(session_id: str, name: str):
    """Clone an existing session"""
    try:
        # Get the source session
        source_session = session_store.get_session(session_id)
        if not source_session:
            raise HTTPException(status_code=404, detail="Source session not found")

        # Create new session with cloned data
        new_session_id = str(uuid.uuid4())
        now = datetime.now()

        new_session = SessionState(
            id=new_session_id,
            name=name,
            created_at=now,
            updated_at=now,
            chat_history=source_session.chat_history,
            editor_files=source_session.editor_files,
            active_filepath=source_session.active_filepath,
            settings=source_session.settings,
            git_branch=source_session.git_branch
        )

        if session_store.create_session(new_session):
            return new_session
        else:
            raise HTTPException(status_code=500, detail="Failed to clone session")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{session_id}/export")
async def export_session(session_id: str):
    """Export session data"""
    try:
        session = session_store.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        return session
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/import")
async def import_session(session_data: SessionState):
    """Import session data"""
    try:
        # Generate new ID for imported session
        session_data.id = str(uuid.uuid4())
        session_data.created_at = datetime.now()
        session_data.updated_at = datetime.now()

        if session_store.create_session(session_data):
            return {"message": "Session imported successfully", "id": session_data.id}
        else:
            raise HTTPException(status_code=500, detail="Failed to import session")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
