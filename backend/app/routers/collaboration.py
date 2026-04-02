from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List
import json
import logging
from ..services.collaboration import collaboration_service

router = APIRouter(prefix="/collaboration")
logger = logging.getLogger(__name__)


class CreateSessionRequest(BaseModel):
    session_name: str
    creator_id: str


class JoinSessionRequest(BaseModel):
    session_id: str
    user_id: str


class FileUpdateRequest(BaseModel):
    session_id: str
    file_path: str
    content: str
    cursor_position: Dict[str, int]
    user_id: str


class ChatMessageRequest(BaseModel):
    session_id: str
    user_id: str
    message: str


class CursorUpdateRequest(BaseModel):
    session_id: str
    user_id: str
    file_path: str
    cursor_position: Dict[str, int]


@router.post("/sessions")
async def create_session(request: CreateSessionRequest):
    """Create a new collaboration session"""
    try:
        session_id = await collaboration_service.create_session(
            request.session_name,
            request.creator_id
        )
        return {"session_id": session_id, "message": "Session created successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception("Failed to create session")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/sessions/join")
async def join_session(request: JoinSessionRequest):
    """Join an existing collaboration session"""
    try:
        success = await collaboration_service.join_session(
            request.session_id,
            request.user_id
        )
        if success:
            return {"message": "Joined session successfully"}
        else:
            raise HTTPException(status_code=404, detail="Session not found")
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Failed to join session")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/sessions/leave")
async def leave_session(request: JoinSessionRequest):
    """Leave a collaboration session"""
    try:
        success = await collaboration_service.leave_session(
            request.session_id,
            request.user_id
        )
        if success:
            return {"message": "Left session successfully"}
        else:
            raise HTTPException(status_code=404, detail="Session not found")
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Failed to leave session")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/sessions/{session_id}")
async def delete_session(session_id: str):
    """Delete a collaboration session"""
    try:
        success = await collaboration_service.delete_session(session_id)
        if success:
            return {"message": "Session deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="Session not found")
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Failed to delete session")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.websocket("/ws/{session_id}/{user_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str, user_id: str):
    """WebSocket endpoint for real-time collaboration"""
    await websocket.accept()

    try:
        await collaboration_service.websocket_manager.connect(websocket, session_id, user_id)

        while True:
            data = await websocket.receive_text()
            message = json.loads(data)

            if message["type"] == "file_update":
                await collaboration_service.sync_file_state(
                    session_id,
                    message["file_path"],
                    message["content"],
                    message["cursor_position"],
                    user_id
                )
            elif message["type"] == "cursor_update":
                await collaboration_service.sync_cursor_position(
                    session_id,
                    user_id,
                    message["file_path"],
                    message["cursor_position"]
                )
            elif message["type"] == "chat_message":
                await collaboration_service.send_chat_message(
                    session_id,
                    user_id,
                    message["message"]
                )

    except WebSocketDisconnect:
        await collaboration_service.websocket_manager.disconnect(session_id, user_id)
    except json.JSONDecodeError as e:
        logger.warning(f"Invalid JSON from user {user_id}: {e}")
        await websocket.send_text(json.dumps({"error": "Invalid JSON format"}))
    except KeyError as e:
        logger.warning(f"Missing field from user {user_id}: {e}")
        await websocket.send_text(json.dumps({"error": f"Missing field: {e}"}))
    except Exception as e:
        logger.exception(f"WebSocket error for user {user_id}")
        await websocket.send_text(json.dumps({"error": "Internal server error"}))
    finally:
        await collaboration_service.websocket_manager.disconnect(session_id, user_id)


@router.get("/sessions/{session_id}")
async def get_session_info(session_id: str):
    """Get information about a collaboration session"""
    try:
        session_info = await collaboration_service.get_session_info(session_id)
        if session_info:
            return session_info
        else:
            raise HTTPException(status_code=404, detail="Session not found")
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Failed to get session info")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/sessions/{session_id}/participants")
async def get_session_participants(session_id: str):
    """Get all participants in a collaboration session"""
    try:
        session_info = await collaboration_service.get_session_info(session_id)
        if session_info:
            return {"participants": session_info.get("participants", [])}
        else:
            raise HTTPException(status_code=404, detail="Session not found")
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Failed to get session participants")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/sessions/{session_id}/chat")
async def get_session_chat(session_id: str):
    """Get chat history for a collaboration session"""
    try:
        session_info = await collaboration_service.get_session_info(session_id)
        if session_info:
            return {"chat": session_info.get("chat", [])}
        else:
            raise HTTPException(status_code=404, detail="Session not found")
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Failed to get session chat")
        raise HTTPException(status_code=500, detail="Internal server error")
