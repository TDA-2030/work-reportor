import os
import logging
from typing import List

logger = logging.getLogger(__name__)


def scan_for_projects(base_dirs: List[str]) -> List[dict]:
    """Scan directories to auto-detect projects."""
    projects = []
    seen = set()

    for base_dir in base_dirs:
        if not os.path.isdir(base_dir):
            continue

        try:
            for entry in os.scandir(base_dir):
                if not entry.is_dir():
                    continue
                if entry.name.startswith("."):
                    continue

                path = entry.path.replace("\\", "/")
                if path in seen:
                    continue
                seen.add(path)

                project_type = _detect_type(entry.path)
                has_git = os.path.isdir(os.path.join(entry.path, ".git"))

                projects.append({
                    "name": entry.name,
                    "path": path,
                    "type": project_type,
                    "has_git": has_git,
                })
        except PermissionError:
            continue

    return projects


def _detect_type(path: str) -> str:
    """Detect project type from files."""
    indicators = {
        "package.json": "node",
        "requirements.txt": "python",
        "setup.py": "python",
        "pyproject.toml": "python",
        "go.mod": "go",
        "Cargo.toml": "rust",
        "pom.xml": "java",
        "build.gradle": "java",
        "*.sln": "dotnet",
        "*.csproj": "dotnet",
    }

    for filename, ptype in indicators.items():
        if "*" in filename:
            # Glob-like match
            ext = filename.replace("*", "")
            for f in os.listdir(path):
                if f.endswith(ext):
                    return ptype
        else:
            if os.path.exists(os.path.join(path, filename)):
                return ptype

    return "unknown"
