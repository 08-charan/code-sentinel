import subprocess
from typing import List, Optional
from pydantic import BaseModel


class GitDiffHunk(BaseModel):
    file_path: str
    change_type: str  # "MODIFIED", "ADDED", "DELETED"
    added_lines: List[str]
    removed_lines: List[str]


class GitInspector:
    """
    Interfaces directly with the local Git VCS repository using subprocess or GitPython.
    Extracts staged changes, working tree diffs, and recently modified files for automated review.
    """

    def __init__(self, repo_root: str = "."):
        self.repo_root = repo_root

    def is_git_repo(self) -> bool:
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--is-inside-work-tree"],
                cwd=self.repo_root,
                capture_output=True,
                text=True,
                check=False,
            )
            return result.returncode == 0 and "true" in result.stdout.strip().lower()
        except FileNotFoundError:
            return False

    def get_staged_files(self) -> List[str]:
        if not self.is_git_repo():
            return []
        res = subprocess.run(
            ["git", "diff", "--name-only", "--cached", "--diff-filter=d"],
            cwd=self.repo_root,
            capture_output=True,
            text=True,
            check=False,
        )
        if res.returncode != 0:
            return []
        return [f.strip() for f in res.stdout.splitlines() if f.strip().endswith(".py")]

    def get_working_diff(self, staged_only: bool = False) -> str:
        if not self.is_git_repo():
            return ""
        cmd = ["git", "diff"]
        if staged_only:
            cmd.append("--cached")
        res = subprocess.run(cmd, cwd=self.repo_root, capture_output=True, text=True, check=False)
        return res.stdout if res.returncode == 0 else ""

    def get_current_branch(self) -> str:
        if not self.is_git_repo():
            return "detached"
        res = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=self.repo_root,
            capture_output=True,
            text=True,
            check=False,
        )
        return res.stdout.strip() if res.returncode == 0 else "unknown"
