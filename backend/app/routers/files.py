from fastapi import APIRouter, UploadFile, File, HTTPException, Query
from typing import List, Optional
import os
import shutil
from pathlib import Path
import mimetypes
import subprocess
from pydantic import BaseModel

router = APIRouter()

# Workspace directory configuration
WORKSPACE_DIR = Path(os.getenv("WORKSPACE_DIR", "./workspace")).resolve()
WORKSPACE_DIR.mkdir(exist_ok=True, parents=True)

class FileInfo(BaseModel):
    name: str
    is_dir: bool
    size: Optional[int] = None
    modified: Optional[float] = None

class FileContent(BaseModel):
    name: str
    content: str
    language: str

class ExecuteResult(BaseModel):
    stdout: str
    stderr: str
    returncode: int

class GitStatus(BaseModel):
    branch: str
    clean: bool
    status: List[str]

def get_language_from_filename(filename: str) -> str:
    """Determine programming language from file extension"""
    mime_type, _ = mimetypes.guess_type(filename)
    if mime_type:
        if 'javascript' in mime_type:
            return 'javascript'
        elif 'python' in mime_type:
            return 'python'
        elif 'html' in mime_type:
            return 'html'
        elif 'css' in mime_type:
            return 'css'
        elif 'json' in mime_type:
            return 'json'
        elif 'markdown' in mime_type:
            return 'markdown'

    # Fallback based on extension
    ext = Path(filename).suffix.lower()
    language_map = {
        '.js': 'javascript',
        '.jsx': 'javascript',
        '.ts': 'typescript',
        '.tsx': 'typescript',
        '.py': 'python',
        '.java': 'java',
        '.cpp': 'cpp',
        '.c': 'c',
        '.cs': 'csharp',
        '.go': 'go',
        '.rs': 'rust',
        '.php': 'php',
        '.rb': 'ruby',
        '.swift': 'swift',
        '.kt': 'kotlin',
        '.sql': 'sql',
        '.sh': 'shell',
        '.yaml': 'yaml',
        '.yml': 'yaml',
        '.xml': 'xml',
        '.md': 'markdown',
        '.txt': 'text'
    }

    return language_map.get(ext, 'text')

@router.get("/list", response_model=List[FileInfo])
async def list_files(path: str = "/"):
    """List all files in workspace or subdirectory"""
    try:
        target_path = WORKSPACE_DIR / path.lstrip("/")
        if not target_path.exists():
            raise HTTPException(status_code=404, detail="Path not found")

        if not target_path.is_dir():
            raise HTTPException(status_code=400, detail="Path is not a directory")

        files = []
        for item in target_path.iterdir():
            stat = item.stat()
            files.append(FileInfo(
                name=item.name,
                is_dir=item.is_dir(),
                size=stat.st_size if not item.is_dir() else None,
                modified=stat.st_mtime
            ))

        # Sort directories first, then files
        files.sort(key=lambda x: (not x.is_dir, x.name.lower()))
        return files
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    path: str = Query("/", description="Destination path")
):
    """Upload a file to workspace"""
    try:
        # Ensure path exists
        target_dir = WORKSPACE_DIR / path.lstrip("/")
        target_dir.mkdir(exist_ok=True, parents=True)

        file_path = target_dir / file.filename
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        return {
            "filename": file.filename,
            "path": str(file_path.relative_to(WORKSPACE_DIR)),
            "status": "uploaded"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/read/{filepath:path}", response_model=FileContent)
async def read_file(filepath: str):
    """Read a file from workspace"""
    try:
        file_path = WORKSPACE_DIR / filepath
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="File not found")

        if file_path.is_dir():
            raise HTTPException(status_code=400, detail="Path is a directory")

        # Read file content
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        language = get_language_from_filename(file_path.name)

        return FileContent(
            name=file_path.name,
            content=content,
            language=language
        )
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="File is not a text file")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/save")
async def save_file(filepath: str, content: str):
    """Save content to a file"""
    try:
        file_path = WORKSPACE_DIR / filepath

        # Create parent directories if they don't exist
        file_path.parent.mkdir(exist_ok=True, parents=True)

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

        language = get_language_from_filename(file_path.name)

        return {
            "filepath": filepath,
            "language": language,
            "status": "saved"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/delete/{filepath:path}")
async def delete_file(filepath: str):
    """Delete a file or directory"""
    try:
        file_path = WORKSPACE_DIR / filepath
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="File or directory not found")

        if file_path.is_dir():
            shutil.rmtree(file_path)
        else:
            file_path.unlink()

        return {"message": "Deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/create-folder")
async def create_folder(filepath: str):
    """Create a new folder"""
    try:
        folder_path = WORKSPACE_DIR / filepath
        folder_path.mkdir(exist_ok=True, parents=True)
        return {"message": "Folder created successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/rename")
async def rename_file(old_path: str, new_path: str):
    """Rename a file or folder"""
    try:
        old_file_path = WORKSPACE_DIR / old_path
        new_file_path = WORKSPACE_DIR / new_path

        if not old_file_path.exists():
            raise HTTPException(status_code=404, detail="File or directory not found")

        # Create parent directories for new path
        new_file_path.parent.mkdir(exist_ok=True, parents=True)

        old_file_path.rename(new_file_path)
        return {"message": "Renamed successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/execute", response_model=ExecuteResult)
async def execute_command(command: str, cwd: str = "/"):
    """Execute a shell command in the workspace"""
    try:
        working_dir = WORKSPACE_DIR / cwd.lstrip("/")
        if not working_dir.exists():
            working_dir = WORKSPACE_DIR

        # Run the command
        result = subprocess.run(
            command,
            shell=True,
            cwd=working_dir,
            capture_output=True,
            text=True,
            timeout=30  # 30 second timeout
        )

        return ExecuteResult(
            stdout=result.stdout,
            stderr=result.stderr,
            returncode=result.returncode
        )
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=408, detail="Command execution timed out")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/git/status", response_model=GitStatus)
async def git_status():
    """Get git repository status"""
    try:
        # Check if git repo exists
        git_dir = WORKSPACE_DIR / ".git"
        if not git_dir.exists():
            return GitStatus(branch="", clean=True, status=["Not a git repository"])

        # Get current branch
        result = subprocess.run(
            ["git", "branch", "--show-current"],
            cwd=WORKSPACE_DIR,
            capture_output=True,
            text=True
        )
        branch = result.stdout.strip()

        # Get status
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=WORKSPACE_DIR,
            capture_output=True,
            text=True
        )
        status_lines = result.stdout.strip().split('\n') if result.stdout.strip() else []
        clean = len(status_lines) == 0

        return GitStatus(
            branch=branch,
            clean=clean,
            status=status_lines
        )
    except FileNotFoundError:
        return GitStatus(branch="", clean=True, status=["Git not installed"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
