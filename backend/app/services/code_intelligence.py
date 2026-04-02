import subprocess
import json
from typing import List, Dict, Any, Optional
from pathlib import Path
import re

class CodeIntelligenceService:
    """Service for providing code intelligence features"""

    def __init__(self, workspace_path: str):
        self.workspace_path = Path(workspace_path)

    def get_diagnostics(self, filepath: str, content: str) -> List[Dict[str, Any]]:
        """Get diagnostics (errors/warnings) for code"""
        try:
            file_path = self.workspace_path / filepath
            extension = file_path.suffix.lower()

            if extension == '.py':
                return self._get_python_diagnostics(filepath, content)
            elif extension in ['.js', '.jsx']:
                return self._get_javascript_diagnostics(filepath, content)
            elif extension in ['.ts', '.tsx']:
                return self._get_typescript_diagnostics(filepath, content)
            else:
                return []
        except Exception as e:
            print(f"Error getting diagnostics: {e}")
            return []

    def get_completions(self, filepath: str, content: str, line: int, character: int) -> List[Dict[str, Any]]:
        """Get code completions at a specific position"""
        try:
            file_path = self.workspace_path / filepath
            extension = file_path.suffix.lower()

            if extension == '.py':
                return self._get_python_completions(filepath, content, line, character)
            elif extension in ['.js', '.jsx', '.ts', '.tsx']:
                return self._get_javascript_completions(filepath, content, line, character)
            else:
                return []
        except Exception as e:
            print(f"Error getting completions: {e}")
            return []

    def get_definitions(self, filepath: str, content: str, line: int, character: int) -> List[Dict[str, Any]]:
        """Get definitions/references for a symbol"""
        try:
            file_path = self.workspace_path / filepath
            extension = file_path.suffix.lower()

            if extension == '.py':
                return self._get_python_definitions(filepath, content, line, character)
            elif extension in ['.js', '.jsx', '.ts', '.tsx']:
                return self._get_javascript_definitions(filepath, content, line, character)
            else:
                return []
        except Exception as e:
            print(f"Error getting definitions: {e}")
            return []

    def get_documentation(self, filepath: str, content: str, line: int, character: int) -> Optional[Dict[str, Any]]:
        """Get documentation for a symbol"""
        try:
            file_path = self.workspace_path / filepath
            extension = file_path.suffix.lower()

            if extension == '.py':
                return self._get_python_documentation(filepath, content, line, character)
            elif extension in ['.js', '.jsx', '.ts', '.tsx']:
                return self._get_javascript_documentation(filepath, content, line, character)
            else:
                return None
        except Exception as e:
            print(f"Error getting documentation: {e}")
            return None

    def format_code(self, filepath: str, content: str) -> str:
        """Format code according to language standards"""
        try:
            file_path = self.workspace_path / filepath
            extension = file_path.suffix.lower()

            if extension == '.py':
                return self._format_python_code(content)
            elif extension in ['.js', '.jsx', '.ts', '.tsx']:
                return self._format_javascript_code(content)
            elif extension == '.json':
                return self._format_json_code(content)
            else:
                return content
        except Exception as e:
            print(f"Error formatting code: {e}")
            return content

    def _get_python_diagnostics(self, filepath: str, content: str) -> List[Dict[str, Any]]:
        """Get Python diagnostics using pylint or flake8"""
        try:
            # Write content to temporary file
            temp_file = self.workspace_path / f".temp_{filepath.replace('/', '_')}"
            temp_file.write_text(content, encoding='utf-8')

            # Run pylint
            result = subprocess.run(
                ['pylint', '--output-format=json', str(temp_file)],
                capture_output=True,
                text=True,
                cwd=self.workspace_path
            )

            # Clean up temp file
            temp_file.unlink(missing_ok=True)

            if result.returncode in [0, 4, 8, 16]:
                try:
                    pylint_output = json.loads(result.stdout)
                    diagnostics = []
                    for item in pylint_output:
                        diagnostics.append({
                            "severity": "warning" if item["type"] == "warning" else "error",
                            "message": f"{item['message']} ({item['symbol']})",
                            "range": {
                                "start": {"line": item["line"] - 1, "character": 0},
                                "end": {"line": item["line"] - 1, "character": 1000}
                            },
                            "source": "pylint"
                        })
                    return diagnostics
                except json.JSONDecodeError:
                    pass

            return []
        except FileNotFoundError:
            return []
        except Exception as e:
            print(f"Error running pylint: {e}")
            return []

    def _get_python_completions(self, filepath: str, content: str, line: int, character: int) -> List[Dict[str, Any]]:
        """Get Python completions using jedi"""
        try:
            import jedi

            script = jedi.Script(code=content, path=str(self.workspace_path / filepath))
            completions = script.complete(line + 1, character)

            result = []
            for completion in completions[:20]:
                result.append({
                    "label": completion.name,
                    "kind": completion.type,
                    "detail": completion.description,
                    "documentation": completion.docstring() or ""
                })

            return result
        except ImportError:
            return []
        except Exception as e:
            print(f"Error getting Python completions: {e}")
            return []

    def _get_python_definitions(self, filepath: str, content: str, line: int, character: int) -> List[Dict[str, Any]]:
        """Get Python definitions using jedi"""
        try:
            import jedi

            script = jedi.Script(code=content, path=str(self.workspace_path / filepath))
            definitions = script.goto(line + 1, character)

            result = []
            for definition in definitions:
                if definition.module_path:
                    result.append({
                        "uri": f"file://{definition.module_path}",
                        "range": {
                            "start": {"line": definition.line - 1, "character": definition.column},
                            "end": {"line": definition.line - 1, "character": definition.column + len(definition.name)}
                        },
                        "name": definition.name
                    })

            return result
        except Exception as e:
            print(f"Error getting Python definitions: {e}")
            return []

    def _get_python_documentation(self, filepath: str, content: str, line: int, character: int) -> Optional[Dict[str, Any]]:
        """Get Python documentation using jedi"""
        try:
            import jedi

            script = jedi.Script(code=content, path=str(self.workspace_path / filepath))
            definitions = script.goto(line + 1, character)

            for definition in definitions:
                doc = definition.docstring()
                if doc:
                    return {
                        "content": doc,
                        "name": definition.name,
                        "source": "python"
                    }

            return None
        except Exception as e:
            print(f"Error getting Python documentation: {e}")
            return None

    def _get_javascript_diagnostics(self, filepath: str, content: str) -> List[Dict[str, Any]]:
        """Get JavaScript/TypeScript diagnostics using eslint"""
        try:
            temp_file = self.workspace_path / f".temp_{filepath.replace('/', '_')}"
            temp_file.write_text(content, encoding='utf-8')

            result = subprocess.run(
                ['npx', 'eslint', '--format=json', str(temp_file)],
                capture_output=True,
                text=True,
                cwd=self.workspace_path,
                timeout=30
            )

            temp_file.unlink(missing_ok=True)

            if result.returncode in [0, 1, 2]:
                try:
                    eslint_output = json.loads(result.stdout)
                    diagnostics = []
                    for file_result in eslint_output:
                        for msg in file_result.get("messages", []):
                            diagnostics.append({
                                "severity": "warning" if msg["severity"] == 1 else "error",
                                "message": msg["message"],
                                "range": {
                                    "start": {"line": msg["line"] - 1, "character": msg["column"] - 1},
                                    "end": {"line": msg["endLine"] - 1 if msg.get("endLine") else msg["line"] - 1, "character": msg["endColumn"] if msg.get("endColumn") else msg["column"]}
                                },
                                "source": "eslint"
                            })
                    return diagnostics
                except json.JSONDecodeError:
                    pass

            return []
        except FileNotFoundError:
            return []
        except Exception as e:
            print(f"Error running eslint: {e}")
            return []

    def _get_javascript_completions(self, filepath: str, content: str, line: int, character: int) -> List[Dict[str, Any]]:
        """Get JavaScript/TypeScript completions"""
        # Basic keyword completions
        keywords = [
            "const", "let", "var", "function", "class", "extends",
            "import", "export", "return", "if", "else", "for", "while",
            "async", "await", "try", "catch", "throw", "new", "this"
        ]

        return [
            {"label": kw, "kind": "keyword", "detail": "JavaScript keyword"}
            for kw in keywords
        ]

    def _get_javascript_definitions(self, filepath: str, content: str, line: int, character: int) -> List[Dict[str, Any]]:
        """Get JavaScript/TypeScript definitions"""
        return []

    def _get_javascript_documentation(self, filepath: str, content: str, line: int, character: int) -> Optional[Dict[str, Any]]:
        """Get JavaScript/TypeScript documentation"""
        return None

    def _get_typescript_diagnostics(self, filepath: str, content: str) -> List[Dict[str, Any]]:
        """Get TypeScript diagnostics using tsc"""
        return self._get_javascript_diagnostics(filepath, content)

    def _format_python_code(self, content: str) -> str:
        """Format Python code using black"""
        try:
            result = subprocess.run(
                ['black', '-'],
                input=content,
                capture_output=True,
                text=True,
                cwd=self.workspace_path
            )
            if result.returncode == 0:
                return result.stdout
        except FileNotFoundError:
            pass
        except Exception as e:
            print(f"Error running black: {e}")
        return content

    def _format_javascript_code(self, content: str) -> str:
        """Format JavaScript/TypeScript code using prettier"""
        try:
            result = subprocess.run(
                ['npx', 'prettier', '--stdin-filepath', 'test.js'],
                input=content,
                capture_output=True,
                text=True,
                cwd=self.workspace_path,
                timeout=30
            )
            if result.returncode == 0:
                return result.stdout
        except FileNotFoundError:
            pass
        except Exception as e:
            print(f"Error running prettier: {e}")
        return content

    def _format_json_code(self, content: str) -> str:
        """Format JSON code"""
        try:
            data = json.loads(content)
            return json.dumps(data, indent=2)
        except json.JSONDecodeError:
            return content
