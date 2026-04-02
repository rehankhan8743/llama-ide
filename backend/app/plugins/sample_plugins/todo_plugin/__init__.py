import re
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from app.plugins.plugin_base import Plugin, PluginManifest, PluginContext, HookName


class TodoItem(BaseModel):
    """Represents a TODO item found in code"""
    file: str
    line: int
    content: str
    severity: str = "info"  # info, warning, error


class TodoPlugin(Plugin):
    """Plugin that tracks TODO comments in code files"""

    manifest = PluginManifest(
        name="todo_plugin",
        version="1.0.0",
        description="Tracks TODO comments in code files",
        author="llama-ide Team",
        keywords=["todo", "task", "productivity"],
        hooks=["file_saved", "file_opened"],
        routes=[],
        dependencies=[]
    )

    def __init__(self):
        self.todos: Dict[str, List[TodoItem]] = {}
        self._context: Optional[PluginContext] = None

    async def initialize(self, context: PluginContext) -> None:
        """Initialize the plugin"""
        self._context = context
        print(f"Initialized {self.manifest.name}")

    async def shutdown(self) -> None:
        """Cleanup when plugin is unloaded"""
        print(f"Shutting down {self.manifest.name}")

    async def on_hook(self, hook_name: HookName, **kwargs) -> Any:
        """Handle hooks"""
        if hook_name == HookName.FILE_SAVED:
            filepath = kwargs.get("filepath")
            content = kwargs.get("content", "")
            if filepath:
                self._scan_file(filepath, content)
        elif hook_name == HookName.FILE_OPENED:
            filepath = kwargs.get("filepath")
            content = kwargs.get("content", "")
            if filepath:
                self._scan_file(filepath, content)
        return None

    def _scan_file(self, filepath: str, content: str) -> None:
        """Scan file for TODO comments"""
        pattern = r'(TODO|FIXME|HACK|XXX|NOTE):?\s*(.*)'
        matches = re.finditer(pattern, content, re.IGNORECASE)

        self.todos[filepath] = []
        for match in matches:
            line_num = content[:match.start()].count('\n') + 1
            todo_type = match.group(1).upper()
            todo_text = match.group(2).strip()

            # Determine severity based on keyword
            severity = "info"
            if todo_type in ("FIXME", "HACK", "XXX"):
                severity = "warning"
            elif todo_type == "TODO":
                severity = "info"

            self.todos[filepath].append(TodoItem(
                file=filepath,
                line=line_num,
                content=f"{todo_type}: {todo_text}" if todo_text else todo_type,
                severity=severity
            ))

    def get_todos(self, filepath: Optional[str] = None) -> Dict[str, List[TodoItem]]:
        """Get todos, optionally filtered by file"""
        if filepath:
            return {filepath: self.todos.get(filepath, [])}
        return self.todos

    def get_all_todos(self) -> List[TodoItem]:
        """Get all todos flattened"""
        result = []
        for todos in self.todos.values():
            result.extend(todos)
        return result
