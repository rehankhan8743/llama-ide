import subprocess
import os
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from pydantic import BaseModel
import json

class GitStatus(BaseModel):
    branch: str
    clean: bool
    status: List[str]
    ahead: int = 0
    behind: int = 0

class GitCommit(BaseModel):
    hash: str
    message: str
    author: str
    date: str
    short_hash: str

class GitBranch(BaseModel):
    name: str
    current: bool
    remote: Optional[str] = None

class GitRemote(BaseModel):
    name: str
    url: str

class GitService:
    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path).resolve()

    def _run_git_command(self, command: List[str], cwd: Optional[str] = None) -> Tuple[str, str, int]:
        """Run a git command and return stdout, stderr, and return code"""
        try:
            process = subprocess.Popen(
                command,
                cwd=cwd or str(self.repo_path),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            stdout, stderr = process.communicate()
            return stdout.strip(), stderr.strip(), process.returncode
        except Exception as e:
            return "", str(e), 1

    def is_git_repo(self) -> bool:
        """Check if the directory is a git repository"""
        stdout, _, returncode = self._run_git_command(["git", "rev-parse", "--git-dir"])
        return returncode == 0

    def init_repo(self) -> bool:
        """Initialize a new git repository"""
        stdout, stderr, returncode = self._run_git_command(["git", "init"])
        return returncode == 0

    def get_status(self) -> GitStatus:
        """Get repository status"""
        if not self.is_git_repo():
            return GitStatus(
                branch="",
                clean=True,
                status=["Not a git repository"],
                ahead=0,
                behind=0
            )

        # Get current branch
        stdout, _, _ = self._run_git_command(["git", "branch", "--show-current"])
        branch = stdout.strip()

        # Get status
        stdout, _, _ = self._run_git_command(["git", "status", "--porcelain"])
        status_lines = stdout.strip().split('\n') if stdout.strip() else []
        clean = len(status_lines) == 0

        # Get ahead/behind info
        stdout, _, _ = self._run_git_command([
            "git", "status", "--porcelain", "--branch"
        ])
        ahead = behind = 0
        if stdout:
            for line in stdout.split('\n'):
                if line.startswith("##"):
                    # Parse ahead/behind info
                    if "ahead" in line:
                        try:
                            ahead = int(line.split("ahead")[1].split()[0])
                        except:
                            pass
                    if "behind" in line:
                        try:
                            behind = int(line.split("behind")[1].split()[0])
                        except:
                            pass

        return GitStatus(
            branch=branch,
            clean=clean,
            status=status_lines,
            ahead=ahead,
            behind=behind
        )

    def stage_file(self, filepath: str) -> bool:
        """Stage a file"""
        stdout, stderr, returncode = self._run_git_command([
            "git", "add", filepath
        ])
        return returncode == 0

    def unstage_file(self, filepath: str) -> bool:
        """Unstage a file"""
        stdout, stderr, returncode = self._run_git_command([
            "git", "reset", "HEAD", filepath
        ])
        return returncode == 0

    def commit(self, message: str, author: Optional[str] = None) -> bool:
        """Commit staged changes"""
        cmd = ["git", "commit", "-m", message]
        if author:
            cmd.extend(["--author", author])

        stdout, stderr, returncode = self._run_git_command(cmd)
        return returncode == 0

    def get_commits(self, limit: int = 10) -> List[GitCommit]:
        """Get recent commits"""
        if not self.is_git_repo():
            return []

        # format: hash|short_hash|author|date|message
        format_str = "%H|%h|%an|%ad|%s"
        stdout, _, returncode = self._run_git_command([
            "git", "log", f"--pretty=format:{format_str}", "-n", str(limit)
        ])

        if returncode != 0 or not stdout:
            return []

        commits = []
        for line in stdout.split('\n'):
            if line:
                parts = line.split('|')
                if len(parts) == 5:
                    commits.append(GitCommit(
                        hash=parts[0],
                        short_hash=parts[1],
                        author=parts[2],
                        date=parts[3],
                        message=parts[4]
                    ))

        return commits

    def get_branches(self) -> List[GitBranch]:
        """Get all branches"""
        if not self.is_git_repo():
            return []

        stdout, _, returncode = self._run_git_command([
            "git", "branch", "--all"
        ])

        if returncode != 0 or not stdout:
            return []

        branches = []
        for line in stdout.split('\n'):
            if line:
                line = line.strip()
                current = line.startswith('*')
                name = line.lstrip('* ').strip()
                remote = None

                if '->' in name:
                    # Remote tracking branch
                    continue

                if name.startswith('remotes/'):
                    remote = name.split('/')[1]
                    name = '/'.join(name.split('/')[2:])

                branches.append(GitBranch(
                    name=name,
                    current=current,
                    remote=remote
                ))

        return branches

    def create_branch(self, branch_name: str) -> bool:
        """Create a new branch"""
        stdout, stderr, returncode = self._run_git_command([
            "git", "checkout", "-b", branch_name
        ])
        return returncode == 0

    def switch_branch(self, branch_name: str) -> bool:
        """Switch to a branch"""
        stdout, stderr, returncode = self._run_git_command([
            "git", "checkout", branch_name
        ])
        return returncode == 0

    def get_remotes(self) -> List[GitRemote]:
        """Get remote repositories"""
        if not self.is_git_repo():
            return []

        stdout, _, returncode = self._run_git_command([
            "git", "remote", "-v"
        ])

        if returncode != 0 or not stdout:
            return []

        remotes = {}
        for line in stdout.split('\n'):
            if line and 'fetch' in line:
                parts = line.split()
                if len(parts) >= 2:
                    name = parts[0]
                    url = parts[1]
                    remotes[name] = GitRemote(name=name, url=url)

        return list(remotes.values())

    def add_remote(self, name: str, url: str) -> bool:
        """Add a remote repository"""
        stdout, stderr, returncode = self._run_git_command([
            "git", "remote", "add", name, url
        ])
        return returncode == 0

    def pull(self, remote: str = "origin", branch: str = "") -> bool:
        """Pull from remote repository"""
        cmd = ["git", "pull", remote]
        if branch:
            cmd.append(branch)

        stdout, stderr, returncode = self._run_git_command(cmd)
        return returncode == 0

    def push(self, remote: str = "origin", branch: str = "") -> bool:
        """Push to remote repository"""
        cmd = ["git", "push", remote]
        if branch:
            cmd.append(branch)

        stdout, stderr, returncode = self._run_git_command(cmd)
        return returncode == 0

    def get_diff(self, filepath: str) -> str:
        """Get diff for a file"""
        stdout, stderr, returncode = self._run_git_command([
            "git", "diff", filepath
        ])
        return stdout if returncode == 0 else ""

    def get_staged_diff(self, filepath: str) -> str:
        """Get staged diff for a file"""
        stdout, stderr, returncode = self._run_git_command([
            "git", "diff", "--cached", filepath
        ])
        return stdout if returncode == 0 else ""
