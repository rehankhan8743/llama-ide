from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import os
from pathlib import Path
from ..services.git_service import GitService, GitStatus, GitCommit, GitBranch, GitRemote

router = APIRouter(prefix="/git")

# Workspace directory
WORKSPACE_DIR = Path(os.getenv("WORKSPACE_DIR", "./workspace")).resolve()

class CommitRequest(BaseModel):
    message: str
    author: Optional[str] = None

class BranchRequest(BaseModel):
    name: str

class RemoteRequest(BaseModel):
    name: str
    url: str

class StageRequest(BaseModel):
    filepath: str

@router.get("/status", response_model=GitStatus)
async def get_status():
    """Get git repository status"""
    try:
        git_service = GitService(WORKSPACE_DIR)
        return git_service.get_status()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/init")
async def init_repo():
    """Initialize a new git repository"""
    try:
        git_service = GitService(WORKSPACE_DIR)
        if git_service.init_repo():
            return {"message": "Repository initialized successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to initialize repository")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/stage", response_model=dict)
async def stage_file(request: StageRequest):
    """Stage a file"""
    try:
        git_service = GitService(WORKSPACE_DIR)
        if git_service.stage_file(request.filepath):
            return {"message": "File staged successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to stage file")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/unstage", response_model=dict)
async def unstage_file(request: StageRequest):
    """Unstage a file"""
    try:
        git_service = GitService(WORKSPACE_DIR)
        if git_service.unstage_file(request.filepath):
            return {"message": "File unstaged successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to unstage file")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/commit", response_model=dict)
async def commit_changes(request: CommitRequest):
    """Commit staged changes"""
    try:
        git_service = GitService(WORKSPACE_DIR)
        if git_service.commit(request.message, request.author):
            return {"message": "Changes committed successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to commit changes")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/commits", response_model=List[GitCommit])
async def get_commits(limit: int = 10):
    """Get recent commits"""
    try:
        git_service = GitService(WORKSPACE_DIR)
        return git_service.get_commits(limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/branches", response_model=List[GitBranch])
async def get_branches():
    """Get all branches"""
    try:
        git_service = GitService(WORKSPACE_DIR)
        return git_service.get_branches()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/branches", response_model=dict)
async def create_branch(request: BranchRequest):
    """Create a new branch"""
    try:
        git_service = GitService(WORKSPACE_DIR)
        if git_service.create_branch(request.name):
            return {"message": f"Branch '{request.name}' created successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to create branch")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/branches/switch", response_model=dict)
async def switch_branch(request: BranchRequest):
    """Switch to a branch"""
    try:
        git_service = GitService(WORKSPACE_DIR)
        if git_service.switch_branch(request.name):
            return {"message": f"Switched to branch '{request.name}'"}
        else:
            raise HTTPException(status_code=500, detail="Failed to switch branch")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/remotes", response_model=List[GitRemote])
async def get_remotes():
    """Get remote repositories"""
    try:
        git_service = GitService(WORKSPACE_DIR)
        return git_service.get_remotes()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/remotes", response_model=dict)
async def add_remote(request: RemoteRequest):
    """Add a remote repository"""
    try:
        git_service = GitService(WORKSPACE_DIR)
        if git_service.add_remote(request.name, request.url):
            return {"message": f"Remote '{request.name}' added successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to add remote")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/pull", response_model=dict)
async def pull_changes(remote: str = "origin", branch: str = ""):
    """Pull from remote repository"""
    try:
        git_service = GitService(WORKSPACE_DIR)
        if git_service.pull(remote, branch):
            return {"message": "Pulled changes successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to pull changes")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/push", response_model=dict)
async def push_changes(remote: str = "origin", branch: str = ""):
    """Push to remote repository"""
    try:
        git_service = GitService(WORKSPACE_DIR)
        if git_service.push(remote, branch):
            return {"message": "Pushed changes successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to push changes")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/diff/{filepath:path}")
async def get_diff(filepath: str, staged: bool = False):
    """Get diff for a file"""
    try:
        git_service = GitService(WORKSPACE_DIR)
        if staged:
            diff = git_service.get_staged_diff(filepath)
        else:
            diff = git_service.get_diff(filepath)
        return {"diff": diff}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
