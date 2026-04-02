"""
Code execution service for running code in isolated environments.
Supports multiple languages with sandboxed execution.
"""

import subprocess
import tempfile
import os
import json
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum


class ExecutionStatus(Enum):
    SUCCESS = "success"
    ERROR = "error"
    TIMEOUT = "timeout"
    MEMORY_EXCEEDED = "memory_exceeded"


@dataclass
class ExecutionResult:
    status: ExecutionStatus
    stdout: str
    stderr: str
    exit_code: int
    execution_time: float
    memory_used: Optional[int] = None


class CodeExecutor:
    """Sandboxed code execution service"""

    # Language to file extension mapping
    EXTENSIONS = {
        "python": ".py",
        "javascript": ".js",
        "typescript": ".ts",
        "java": ".java",
        "cpp": ".cpp",
        "c": ".c",
        "go": ".go",
        "rust": ".rs",
        "ruby": ".rb",
        "php": ".php",
        "bash": ".sh",
    }

    # Language interpreters/compilers
    RUNTIMES = {
        "python": ["python3"],
        "javascript": ["node"],
        "typescript": ["npx", "ts-node"],
        "java": ["java"],
        "go": ["go", "run"],
        "rust": ["rustc"],
        "ruby": ["ruby"],
        "php": ["php"],
        "bash": ["bash"],
    }

    def __init__(self, workspace_dir: str = "./workspace"):
        self.workspace_dir = Path(workspace_dir)
        self.workspace_dir.mkdir(exist_ok=True)
        self.active_processes: Dict[str, subprocess.Popen] = {}

    async def execute(
        self,
        code: str,
        language: str,
        timeout: int = 30,
        stdin: Optional[str] = None,
        env_vars: Optional[Dict[str, str]] = None,
    ) -> ExecutionResult:
        """
        Execute code in a sandboxed environment.

        Args:
            code: The code to execute
            language: Programming language
            timeout: Maximum execution time in seconds
            stdin: Input to provide to the program
            env_vars: Additional environment variables

        Returns:
            ExecutionResult with output and status
        """
        if language not in self.EXTENSIONS:
            return ExecutionResult(
                status=ExecutionStatus.ERROR,
                stdout="",
                stderr=f"Unsupported language: {language}",
                exit_code=-1,
                execution_time=0.0,
            )

        # Create temporary file
        ext = self.EXTENSIONS[language]
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=ext,
            dir=self.workspace_dir,
            delete=False,
        ) as f:
            f.write(code)
            temp_path = f.name

        try:
            result = await self._run_code(
                temp_path, language, timeout, stdin, env_vars
            )
            return result
        finally:
            # Cleanup
            try:
                os.unlink(temp_path)
            except:
                pass

    async def _run_code(
        self,
        file_path: str,
        language: str,
        timeout: int,
        stdin: Optional[str],
        env_vars: Optional[Dict[str, str]],
    ) -> ExecutionResult:
        """Run the code file"""
        import time

        runtime = self.RUNTIMES.get(language, [])
        if not runtime:
            return ExecutionResult(
                status=ExecutionStatus.ERROR,
                stdout="",
                stderr=f"No runtime configured for {language}",
                exit_code=-1,
                execution_time=0.0,
            )

        # Prepare environment
        env = os.environ.copy()
        if env_vars:
            env.update(env_vars)

        # Build command
        cmd = runtime + [file_path]

        start_time = time.time()
        try:
            process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE if stdin else None,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env=env,
                cwd=str(self.workspace_dir),
            )

            stdout, stderr = process.communicate(
                input=stdin, timeout=timeout
            )

            execution_time = time.time() - start_time

            return ExecutionResult(
                status=ExecutionStatus.SUCCESS if process.returncode == 0 else ExecutionStatus.ERROR,
                stdout=stdout,
                stderr=stderr,
                exit_code=process.returncode,
                execution_time=execution_time,
            )

        except subprocess.TimeoutExpired:
            process.kill()
            return ExecutionResult(
                status=ExecutionStatus.TIMEOUT,
                stdout="",
                stderr=f"Execution timed out after {timeout} seconds",
                exit_code=-1,
                execution_time=timeout,
            )

        except Exception as e:
            return ExecutionResult(
                status=ExecutionStatus.ERROR,
                stdout="",
                stderr=str(e),
                exit_code=-1,
                execution_time=time.time() - start_time,
            )

    async def execute_test(
        self,
        code: str,
        test_code: str,
        language: str,
        framework: Optional[str] = None,
        timeout: int = 60,
    ) -> ExecutionResult:
        """Execute code with tests"""
        combined_code = f"""
{code}

# Test code
{test_code}
"""
        return await self.execute(combined_code, language, timeout)

    def validate_code(self, code: str, language: str) -> Dict[str, Any]:
        """Validate code without executing"""
        # Basic syntax validation
        errors = []
        warnings = []

        if language == "python":
            import ast
            try:
                ast.parse(code)
            except SyntaxError as e:
                errors.append(str(e))

            # Check for dangerous imports
            dangerous = ["os.system", "subprocess.call", "eval", "exec"]
            for d in dangerous:
                if d in code:
                    warnings.append(f"Potentially dangerous function: {d}")

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
        }

    def format_code(self, code: str, language: str) -> str:
        """Format code using available formatters"""
        formatters = {
            "python": ["black", "-"],
            "javascript": ["prettier", "--stdin-filepath", "file.js"],
            "typescript": ["prettier", "--stdin-filepath", "file.ts"],
        }

        if language not in formatters:
            return code

        try:
            result = subprocess.run(
                formatters[language],
                input=code,
                capture_output=True,
                text=True,
                timeout=10,
            )
            return result.stdout if result.returncode == 0 else code
        except:
            return code

    async def lint_code(self, code: str, language: str) -> List[Dict[str, Any]]:
        """Run linter on code"""
        linters = {
            "python": ["pylint", "--from-stdin", "code", "-f", "json"],
            "javascript": ["eslint", "--stdin", "--format", "json"],
            "typescript": ["eslint", "--stdin", "--format", "json"],
        }

        if language not in linters:
            return []

        try:
            result = subprocess.run(
                linters[language],
                input=code,
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode == 0:
                return []

            # Parse linter output
            return [{"message": result.stderr or "Unknown error"}]
        except:
            return []


# Global executor instance
_executor: Optional[CodeExecutor] = None


def get_executor() -> CodeExecutor:
    """Get or create global executor instance"""
    global _executor
    if _executor is None:
        _executor = CodeExecutor()
    return _executor
