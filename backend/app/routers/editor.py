from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import os
import subprocess
from pathlib import Path
from ..services.code_intelligence import CodeIntelligenceService

router = APIRouter(prefix="/editor")

# Workspace directory
WORKSPACE_DIR = Path(os.getenv("WORKSPACE_DIR", "./workspace")).resolve()

# Initialize code intelligence service
code_intelligence = CodeIntelligenceService(str(WORKSPACE_DIR))

class DiagnosticsRequest(BaseModel):
    filepath: str
    content: str

class CompletionsRequest(BaseModel):
    filepath: str
    content: str
    line: int
    character: int

class DefinitionsRequest(BaseModel):
    filepath: str
    content: str
    line: int
    character: int

class DocumentationRequest(BaseModel):
    filepath: str
    content: str
    line: int
    character: int

class FormatRequest(BaseModel):
    filepath: str
    content: str

class DebugRequest(BaseModel):
    filepath: str
    breakpoints: Optional[List[Dict[str, Any]]] = None

class TestRequest(BaseModel):
    test_pattern: Optional[str] = None

class Diagnostic(BaseModel):
    severity: str
    message: str
    range: Dict[str, Any]
    source: str

class Completion(BaseModel):
    label: str
    kind: str
    detail: Optional[str] = None
    documentation: Optional[str] = None

class Definition(BaseModel):
    uri: str
    range: Dict[str, Any]
    name: str

class Documentation(BaseModel):
    content: Optional[str] = None
    name: Optional[str] = None
    source: Optional[str] = None

@router.post("/diagnostics", response_model=List[Diagnostic])
async def get_diagnostics(request: DiagnosticsRequest):
    """Get diagnostics for a file"""
    try:
        diagnostics = code_intelligence.get_diagnostics(request.filepath, request.content)
        return diagnostics
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/completions", response_model=List[Completion])
async def get_completions(request: CompletionsRequest):
    """Get code completions at a position"""
    try:
        completions = code_intelligence.get_completions(
            request.filepath,
            request.content,
            request.line,
            request.character
        )
        return completions
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/definitions", response_model=List[Definition])
async def get_definitions(request: DefinitionsRequest):
    """Get definitions for a symbol"""
    try:
        definitions = code_intelligence.get_definitions(
            request.filepath,
            request.content,
            request.line,
            request.character
        )
        return definitions
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/documentation")
async def get_documentation(request: DocumentationRequest):
    """Get documentation for a symbol"""
    try:
        documentation = code_intelligence.get_documentation(
            request.filepath,
            request.content,
            request.line,
            request.character
        )
        if documentation:
            return documentation
        else:
            return {"content": None}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/format")
async def format_code(request: FormatRequest):
    """Format code"""
    try:
        formatted = code_intelligence.format_code(request.filepath, request.content)
        return {"formatted_content": formatted}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/debug")
async def debug_code(request: DebugRequest):
    """Debug code execution"""
    try:
        file_path = WORKSPACE_DIR / request.filepath
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="File not found")

        # Determine interpreter based on file extension
        ext = file_path.suffix.lower()
        if ext == '.py':
            cmd = ['python', str(file_path)]
        elif ext in ['.js']:
            cmd = ['node', str(file_path)]
        elif ext in ['.ts', '.tsx']:
            cmd = ['npx', 'ts-node', str(file_path)]
        else:
            raise HTTPException(status_code=400, detail="Unsupported file type for debugging")

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30,
            cwd=WORKSPACE_DIR
        )

        return {
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode
        }
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=408, detail="Execution timed out")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/test")
async def run_tests(request: TestRequest = None):
    """Run tests"""
    try:
        test_pattern = request.test_pattern if request else None
        cmd = ['python', '-m', 'pytest']

        if test_pattern:
            cmd.extend(['-k', test_pattern])

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60,
            cwd=WORKSPACE_DIR
        )

        passed = result.returncode == 0

        return {
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode,
            "passed": passed,
            "summary": {}
        }
    except FileNotFoundError:
        return {
            "stdout": "",
            "stderr": "pytest not installed",
            "returncode": 1,
            "passed": False,
            "summary": {},
            "error": "pytest not installed"
        }
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=408, detail="Test execution timed out")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
