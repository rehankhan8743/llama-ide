import sqlite3
import json
from typing import List, Optional, Dict, Any
from datetime import datetime
from pathlib import Path
from ..models.session import SessionState, ChatMessage, EditorFileState

class SessionStore:
    def __init__(self, db_path: str = "sessions.db"):
        self.db_path = Path(db_path)
        self.init_db()

    def init_db(self):
        """Initialize the database with required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                created_at TIMESTAMP NOT NULL,
                updated_at TIMESTAMP NOT NULL,
                chat_history TEXT,
                editor_files TEXT,
                active_filepath TEXT,
                settings TEXT,
                git_branch TEXT
            )
        """)

        conn.commit()
        conn.close()

    def create_session(self, session: SessionState) -> bool:
        """Create a new session"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO sessions
                (id, name, created_at, updated_at, chat_history, editor_files, active_filepath, settings, git_branch)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                session.id,
                session.name,
                session.created_at.isoformat(),
                session.updated_at.isoformat(),
                json.dumps([msg.dict() for msg in session.chat_history]),
                json.dumps([file.dict() for file in session.editor_files]),
                session.active_filepath,
                json.dumps(session.settings),
                session.git_branch
            ))

            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error creating session: {e}")
            return False

    def get_session(self, session_id: str) -> Optional[SessionState]:
        """Get a session by ID"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute("SELECT * FROM sessions WHERE id = ?", (session_id,))
            row = cursor.fetchone()
            conn.close()

            if not row:
                return None

            return SessionState(
                id=row["id"],
                name=row["name"],
                created_at=datetime.fromisoformat(row["created_at"]),
                updated_at=datetime.fromisoformat(row["updated_at"]),
                chat_history=[ChatMessage(**msg) for msg in json.loads(row["chat_history"] or "[]")],
                editor_files=[EditorFileState(**file) for file in json.loads(row["editor_files"] or "[]")],
                active_filepath=row["active_filepath"],
                settings=json.loads(row["settings"] or "{}"),
                git_branch=row["git_branch"]
            )
        except Exception as e:
            print(f"Error getting session: {e}")
            return None

    def update_session(self, session: SessionState) -> bool:
        """Update an existing session"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                UPDATE sessions SET
                name = ?,
                updated_at = ?,
                chat_history = ?,
                editor_files = ?,
                active_filepath = ?,
                settings = ?,
                git_branch = ?
                WHERE id = ?
            """, (
                session.name,
                session.updated_at.isoformat(),
                json.dumps([msg.dict() for msg in session.chat_history]),
                json.dumps([file.dict() for file in session.editor_files]),
                session.active_filepath,
                json.dumps(session.settings),
                session.git_branch,
                session.id
            ))

            conn.commit()
            conn.close()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"Error updating session: {e}")
            return False

    def delete_session(self, session_id: str) -> bool:
        """Delete a session"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("DELETE FROM sessions WHERE id = ?", (session_id,))

            conn.commit()
            conn.close()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"Error deleting session: {e}")
            return False

    def list_sessions(self) -> List[Dict[str, Any]]:
        """List all sessions (summary info only)"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute("""
                SELECT id, name, created_at, updated_at
                FROM sessions
                ORDER BY updated_at DESC
            """)

            rows = cursor.fetchall()
            conn.close()

            return [{
                "id": row["id"],
                "name": row["name"],
                "created_at": datetime.fromisoformat(row["created_at"]),
                "updated_at": datetime.fromisoformat(row["updated_at"])
            } for row in rows]
        except Exception as e:
            print(f"Error listing sessions: {e}")
            return []

    def session_exists(self, session_id: str) -> bool:
        """Check if a session exists"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("SELECT 1 FROM sessions WHERE id = ?", (session_id,))
            result = cursor.fetchone()
            conn.close()

            return result is not None
        except Exception as e:
            print(f"Error checking session existence: {e}")
            return False
