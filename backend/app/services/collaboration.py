import asyncio
import json
import logging
from typing import Dict, List, Optional
from datetime import datetime
from dataclasses import dataclass, field
from uuid import uuid4

logger = logging.getLogger(__name__)


@dataclass
class CursorPosition:
    file: str
    line: int
    column: int


@dataclass
class FileState:
    content: str
    last_modified_by: str
    last_modified_at: str
    cursors: Dict[str, CursorPosition] = field(default_factory=dict)


@dataclass
class ChatMessage:
    id: str
    user_id: str
    message: str
    timestamp: str


@dataclass
class Session:
    id: str
    name: str
    creator: str
    created_at: datetime
    participants: List[str]
    files: Dict[str, FileState] = field(default_factory=dict)
    chat: List[ChatMessage] = field(default_factory=list)
    cursors: Dict[str, CursorPosition] = field(default_factory=dict)


class WebSocketManager:
    def __init__(self):
        self.connections: Dict[str, Dict[str, "asyncio.WebSocketServerProtocol"]] = {}
        self.rooms: Dict[str, List[str]] = {}
        self._lock = asyncio.Lock()

    async def connect(
        self, websocket: "asyncio.WebSocketServerProtocol", session_id: str, user_id: str
    ) -> None:
        """Connect user to collaboration session."""
        async with self._lock:
            if session_id not in self.connections:
                self.connections[session_id] = {}
            self.connections[session_id][user_id] = websocket

            if session_id not in self.rooms:
                self.rooms[session_id] = []
            if user_id not in self.rooms[session_id]:
                self.rooms[session_id].append(user_id)

        await self._broadcast(session_id, {
            "type": "user_joined",
            "user_id": user_id,
            "timestamp": datetime.now().isoformat()
        })

    async def disconnect(self, session_id: str, user_id: str) -> None:
        """Disconnect user from collaboration session."""
        async with self._lock:
            if session_id in self.connections:
                self.connections[session_id].pop(user_id, None)
            if session_id in self.rooms and user_id in self.rooms[session_id]:
                self.rooms[session_id].remove(user_id)

        await self._broadcast(session_id, {
            "type": "user_left",
            "user_id": user_id,
            "timestamp": datetime.now().isoformat()
        })

    async def _broadcast(self, session_id: str, message: dict) -> None:
        """Broadcast message to all users in session (internal, no lock)."""
        if session_id not in self.connections:
            return

        disconnected = []
        async with self._lock:
            connections_snapshot = dict(self.connections.get(session_id, {}))

        for user_id, websocket in connections_snapshot.items():
            try:
                await websocket.send(json.dumps(message))
            except Exception as e:
                logger.warning("Error broadcasting to %s: %s", user_id, e)
                disconnected.append(user_id)

        if disconnected:
            async with self._lock:
                for user_id in disconnected:
                    self.connections[session_id].pop(user_id, None)
                    if session_id in self.rooms and user_id in self.rooms[session_id]:
                        self.rooms[session_id].remove(user_id)

    async def send_to_user(self, session_id: str, user_id: str, message: dict) -> bool:
        """Send message to specific user. Returns True if sent successfully."""
        async with self._lock:
            websocket = self.connections.get(session_id, {}).get(user_id)

        if websocket is None:
            return False

        try:
            await websocket.send(json.dumps(message))
            return True
        except Exception as e:
            logger.warning("Error sending to %s: %s", user_id, e)
            return False

    async def close_session(self, session_id: str) -> None:
        """Close all connections for a session."""
        async with self._lock:
            self.connections.pop(session_id, None)
            self.rooms.pop(session_id, None)


class CollaborationService:
    def __init__(self):
        self.websocket_manager = WebSocketManager()
        self.sessions: Dict[str, Session] = {}
        self._lock = asyncio.Lock()

    async def create_session(self, session_name: str, creator_id: str) -> str:
        """Create a new collaboration session."""
        session_id = str(uuid4())
        async with self._lock:
            self.sessions[session_id] = Session(
                id=session_id,
                name=session_name,
                creator=creator_id,
                created_at=datetime.now(),
                participants=[creator_id],
            )
        return session_id

    async def join_session(self, session_id: str, user_id: str) -> bool:
        """Add user to collaboration session."""
        async with self._lock:
            session = self.sessions.get(session_id)
            if session is None:
                return False
            if user_id not in session.participants:
                session.participants.append(user_id)
            return True

    async def leave_session(self, session_id: str, user_id: str) -> bool:
        """Remove user from collaboration session."""
        async with self._lock:
            session = self.sessions.get(session_id)
            if session is None:
                return False
            if user_id in session.participants:
                session.participants.remove(user_id)
            return True

    async def sync_file_state(
        self,
        session_id: str,
        file_path: str,
        content: str,
        cursor_position: Dict[str, int],
        user_id: str,
    ) -> None:
        """Sync file state across participants."""
        async with self._lock:
            session = self.sessions.get(session_id)
            if session is None:
                return

            session.files[file_path] = FileState(
                content=content,
                last_modified_by=user_id,
                last_modified_at=datetime.now().isoformat(),
            )
            session.cursors[user_id] = CursorPosition(
                file=file_path,
                line=cursor_position.get("line", 0),
                column=cursor_position.get("column", 0),
            )

        await self.websocket_manager._broadcast(session_id, {
            "type": "file_update",
            "file_path": file_path,
            "content": content,
            "cursor_position": cursor_position,
            "user_id": user_id,
            "timestamp": datetime.now().isoformat(),
        })

    async def sync_cursor_position(
        self, session_id: str, user_id: str, file_path: str, cursor_position: Dict[str, int]
    ) -> None:
        """Sync cursor position for a user."""
        async with self._lock:
            session = self.sessions.get(session_id)
            if session is None:
                return

            session.cursors[user_id] = CursorPosition(
                file=file_path,
                line=cursor_position.get("line", 0),
                column=cursor_position.get("column", 0),
            )

        await self.websocket_manager._broadcast(session_id, {
            "type": "cursor_update",
            "user_id": user_id,
            "file_path": file_path,
            "cursor_position": cursor_position,
            "timestamp": datetime.now().isoformat(),
        })

    async def send_chat_message(self, session_id: str, user_id: str, message: str) -> bool:
        """Send chat message in collaboration session."""
        async with self._lock:
            session = self.sessions.get(session_id)
            if session is None:
                return False

            chat_message = ChatMessage(
                id=str(uuid4()),
                user_id=user_id,
                message=message,
                timestamp=datetime.now().isoformat(),
            )
            session.chat.append(chat_message)

        await self.websocket_manager._broadcast(session_id, {
            "type": "chat_message",
            "message": {
                "id": chat_message.id,
                "user_id": chat_message.user_id,
                "message": chat_message.message,
                "timestamp": chat_message.timestamp,
            }
        })
        return True

    def get_session_info(self, session_id: str) -> Optional[Session]:
        """Get collaboration session information."""
        return self.sessions.get(session_id)

    async def delete_session(self, session_id: str) -> bool:
        """Delete a collaboration session."""
        async with self._lock:
            if session_id not in self.sessions:
                return False
            del self.sessions[session_id]

        await self.websocket_manager.close_session(session_id)
        return True


# Global collaboration service instance
collaboration_service = CollaborationService()
