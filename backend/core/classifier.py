import re
from typing import Optional

# Default app category mapping
DEFAULT_APP_CATEGORIES = {
    "Code": "开发",
    "code": "开发",
    "devenv": "开发",
    "idea64": "开发",
    "pycharm64": "开发",
    "webstorm64": "开发",
    "goland64": "开发",
    "rider64": "开发",
    "Visual Studio": "开发",
    "WindowsTerminal": "开发",
    "cmd": "开发",
    "powershell": "开发",
    "bash": "开发",
    "mintty": "开发",
    "chrome": "浏览器",
    "msedge": "浏览器",
    "firefox": "浏览器",
    "brave": "浏览器",
    "WINWORD": "文档",
    "EXCEL": "文档",
    "POWERPNT": "文档",
    "Typora": "文档",
    "Obsidian": "文档",
    "Notion": "文档",
    "notepad++": "文档",
    "Notepad": "文档",
    "WeChat": "通讯",
    "DingTalk": "通讯",
    "Telegram": "通讯",
    "Slack": "通讯",
    "Teams": "通讯",
    "QQ": "通讯",
    "Feishu": "通讯",
    "lark": "通讯",
    "explorer": "系统",
    "SearchHost": "系统",
    "Taskmgr": "系统",
    "SystemSettings": "系统",
}

# File extension category mapping
DEFAULT_FILE_CATEGORIES = {
    ".py": "开发",
    ".js": "开发",
    ".ts": "开发",
    ".tsx": "开发",
    ".jsx": "开发",
    ".vue": "开发",
    ".go": "开发",
    ".rs": "开发",
    ".java": "开发",
    ".c": "开发",
    ".cpp": "开发",
    ".h": "开发",
    ".cs": "开发",
    ".rb": "开发",
    ".php": "开发",
    ".swift": "开发",
    ".kt": "开发",
    ".html": "开发",
    ".css": "开发",
    ".scss": "开发",
    ".less": "开发",
    ".json": "配置",
    ".yaml": "配置",
    ".yml": "配置",
    ".toml": "配置",
    ".ini": "配置",
    ".xml": "配置",
    ".md": "文档",
    ".txt": "文档",
    ".doc": "文档",
    ".docx": "文档",
    ".pdf": "文档",
    ".ppt": "文档",
    ".pptx": "文档",
    ".xls": "文档",
    ".xlsx": "文档",
}


class Classifier:
    def __init__(self):
        self.app_categories = dict(DEFAULT_APP_CATEGORIES)
        self.file_categories = dict(DEFAULT_FILE_CATEGORIES)
        self._projects = {}  # name -> path

    def set_projects(self, projects: dict):
        """Set project mapping: name -> path."""
        self._projects = projects

    def add_project(self, name: str, path: str):
        self._projects[name] = path.replace("\\", "/")

    def classify_app(self, app_name: str, window_title: str = "") -> str:
        # Direct match
        if app_name in self.app_categories:
            return self.app_categories[app_name]

        # Case-insensitive match
        app_lower = app_name.lower()
        for key, cat in self.app_categories.items():
            if key.lower() == app_lower:
                return cat

        # Browser with dev-related title
        if app_lower in ("chrome", "msedge", "firefox", "brave"):
            title_lower = window_title.lower()
            dev_keywords = ["github", "stackoverflow", "gitlab", "npm", "docs", "api",
                            "developer", "console", "localhost"]
            for kw in dev_keywords:
                if kw in title_lower:
                    return "调研"
            return "浏览器"

        return "其他"

    def classify_file(self, ext: str) -> str:
        return self.file_categories.get(ext.lower(), "其他")

    def detect_project(self, window_title: str) -> str:
        """Detect project from window title."""
        if not window_title:
            return ""

        # Try to match project paths in window title
        for name, path in self._projects.items():
            if name.lower() in window_title.lower() or path in window_title:
                return name

        # Try to extract from common IDE title patterns
        # VSCode: "filename - project_folder - Visual Studio Code"
        # PyCharm: "project_name – filename"
        patterns = [
            r"- ([^-]+) - Visual Studio Code",
            r"^([^–]+?)(?:\s*–)",
            r"\[(.+?)\]",
        ]
        for pattern in patterns:
            m = re.search(pattern, window_title)
            if m:
                candidate = m.group(1).strip()
                for name in self._projects:
                    if name.lower() == candidate.lower():
                        return name

        return ""

    def detect_project_from_path(self, file_path: str) -> str:
        """Detect project from file path."""
        normalized = file_path.replace("\\", "/")
        for name, path in self._projects.items():
            proj_path = path.replace("\\", "/")
            if normalized.startswith(proj_path + "/") or normalized.startswith(proj_path + "\\"):
                return name
        return ""
