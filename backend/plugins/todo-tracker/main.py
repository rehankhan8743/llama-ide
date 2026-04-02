"""
Todo Tracker Plugin for Llama IDE
Tracks TODOs, FIXMEs, and other task markers in your codebase
"""

import re
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime


class TodoPlugin:
    """Plugin for tracking todos in code"""

    # Patterns to search for
    TODO_PATTERNS = [
        r'#\s*TODO[:\s]+(.+)',           # Python/Shell
        r'//\s*TODO[:\s]+(.+)',          # JavaScript/C/Java
        r'/\*\s*TODO[:\s]+(.+)',         # CSS block
        r'<!--\s*TODO[:\s]+(.+)',        # HTML
        r'\{\s*[#%]\s*TODO[:\s]+(.+)',  # Template
        r'#\s*FIXME[:\s]+(.+)',         # Python FIXME
        r'//\s*FIXME[:\s]+(.+)',        # JS FIXME
        r'\*\s*@todo\s+(.+)',           # JSDoc
    ]

    def __init__(self):
        self.todos: List[Dict[str, Any]] = []
        self.data_file = Path("./plugins/todo-tracker/todos.json")
        self.data_file.parent.mkdir(exist_ok=True)
        self.load_todos()

    def initialize(self, context: Any) -> None:
        """Initialize the plugin"""
        print("Todo Tracker plugin initialized")

    def on_file_save(self, filepath: str, content: str) -> None:
        """Scan file for todos on save"""
        self.scan_file(filepath, content)

    def on_comment_detect(self, filepath: str, comment: str, line: int) -> None:
        """Check individual comments for todos"""
        for pattern in self.TODO_PATTERNS:
            match = re.search(pattern, comment, re.IGNORECASE)
            if match:
                todo_text = match.group(1).strip()
                self.add_todo({
                    "text": todo_text,
                    "file": filepath,
                    "line": line,
                    "type": "TODO",
                    "created": datetime.now().isoformat(),
                    "completed": False,
                })

    def scan_file(self, filepath: str, content: str) -> None:
        """Scan file content for todos"""
        lines = content.split('\n')
        for line_num, line in enumerate(lines, 1):
            for pattern in self.TODO_PATTERNS:
                match = re.search(pattern, line, re.IGNORECASE)
                if match:
                    todo_text = match.group(1).strip()
                    # Check if already exists
                    exists = any(
                        t["file"] == filepath and t["line"] == line_num
                        for t in self.todos
                    )
                    if not exists:
                        self.add_todo({
                            "text": todo_text,
                            "file": filepath,
                            "line": line_num,
                            "type": self._get_todo_type(line),
                            "created": datetime.now().isoformat(),
                            "completed": False,
                        })

    def _get_todo_type(self, line: str) -> str:
        """Determine todo type from line"""
        if 'FIXME' in line.upper():
            return 'FIXME'
        if 'HACK' in line.upper():
            return 'HACK'
        if 'BUG' in line.upper():
            return 'BUG'
        if 'NOTE' in line.upper():
            return 'NOTE'
        return 'TODO'

    def add_todo(self, todo: Dict[str, Any]) -> None:
        """Add a todo item"""
        self.todos.append(todo)
        self.save_todos()

    def complete_todo(self, todo_id: int) -> bool:
        """Mark a todo as completed"""
        if 0 <= todo_id < len(self.todos):
            self.todos[todo_id]["completed"] = True
            self.todos[todo_id]["completed_at"] = datetime.now().isoformat()
            self.save_todos()
            return True
        return False

    def remove_todo(self, todo_id: int) -> bool:
        """Remove a todo"""
        if 0 <= todo_id < len(self.todos):
            self.todos.pop(todo_id)
            self.save_todos()
            return True
        return False

    def get_todos(self, completed: bool = None, file: str = None) -> List[Dict[str, Any]]:
        """Get todos, optionally filtered"""
        todos = self.todos
        if completed is not None:
            todos = [t for t in todos if t["completed"] == completed]
        if file:
            todos = [t for t in todos if t["file"] == file]
        return todos

    def get_stats(self) -> Dict[str, int]:
        """Get todo statistics"""
        total = len(self.todos)
        completed = len([t for t in self.todos if t["completed"]])
        pending = total - completed
        return {
            "total": total,
            "completed": completed,
            "pending": pending,
        }

    def save_todos(self) -> None:
        """Save todos to file"""
        import json
        with open(self.data_file, 'w') as f:
            json.dump(self.todos, f, indent=2)

    def load_todos(self) -> None:
        """Load todos from file"""
        import json
        if self.data_file.exists():
            with open(self.data_file, 'r') as f:
                self.todos = json.load(f)

    def get_manifest(self) -> Dict[str, Any]:
        """Get plugin manifest"""
        return {
            "name": "Todo Tracker",
            "version": "1.0.0",
            "description": "Track TODOs in your codebase",
        }
