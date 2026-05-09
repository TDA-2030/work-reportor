import logging
import threading
import time
from datetime import datetime
from typing import List

logger = logging.getLogger(__name__)


class GitCollector:
    def __init__(self, interval: int = 300):
        self.interval = interval
        self._running = False
        self._thread = None
        self._on_event = None
        self._known_hashes = set()
        self._repo_paths: List[str] = []

    def set_callback(self, callback):
        self._on_event = callback

    def set_repos(self, paths: List[str]):
        self._repo_paths = paths

    def add_repo(self, path: str):
        if path not in self._repo_paths:
            self._repo_paths.append(path)

    def set_known_hashes(self, hashes: set):
        self._known_hashes = hashes

    def start(self):
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()
        logger.info("Git collector started")

    def stop(self):
        self._running = False
        if self._thread:
            self._thread.join(timeout=5)
        logger.info("Git collector stopped")

    def scan_now(self):
        """Manually trigger a scan."""
        for path in self._repo_paths:
            self._scan_repo(path)

    def _run(self):
        # Initial scan
        self.scan_now()
        while self._running:
            time.sleep(self.interval)
            if self._running:
                self.scan_now()

    def _scan_repo(self, repo_path: str):
        try:
            import git

            repo = git.Repo(repo_path)
            project_name = repo_path.replace("\\", "/").rstrip("/").split("/")[-1]

            for commit in repo.iter_commits(max_count=50):
                hash_str = commit.hexsha
                if hash_str in self._known_hashes:
                    continue

                self._known_hashes.add(hash_str)

                # Get stats
                stats = commit.stats.total
                event = {
                    "project": project_name,
                    "repo_path": repo_path,
                    "commit_hash": hash_str,
                    "message": commit.message.strip().split("\n")[0],
                    "timestamp": datetime.fromtimestamp(
                        commit.committed_date
                    ).strftime("%Y-%m-%d %H:%M:%S"),
                    "files_changed": stats.get("files", 0),
                    "insertions": stats.get("insertions", 0),
                    "deletions": stats.get("deletions", 0),
                }

                if self._on_event:
                    self._on_event(event)

        except Exception as e:
            logger.error(f"Failed to scan git repo {repo_path}: {e}")
