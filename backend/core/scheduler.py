import logging
import yaml
import os
from ..collectors.window_collector import WindowCollector
from ..collectors.file_collector import FileCollector
from ..collectors.git_collector import GitCollector
from ..core.classifier import Classifier
from ..core.event import on_window_event, on_file_event, on_git_event
from ..storage.database import get_session
from ..storage.models import Project, GitEvent

logger = logging.getLogger(__name__)

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "config.yaml")


class Scheduler:
    def __init__(self):
        self.window_collector = None
        self.file_collector = None
        self.git_collector = None
        self.classifier = Classifier()

    def load_config(self) -> dict:
        if os.path.exists(CONFIG_PATH):
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        return {}

    def start(self):
        config = self.load_config()

        # Load projects from DB
        try:
            session = get_session()
            projects = session.query(Project).all()
            for p in projects:
                self.classifier.add_project(p.name, p.path)
            session.close()
        except Exception as e:
            logger.error(f"Failed to load projects: {e}")

        # Start window collector
        collector_config = config.get("collectors", {})
        window_config = collector_config.get("window", {})
        if window_config.get("enabled", True):
            self.window_collector = WindowCollector(
                interval=window_config.get("interval", 3)
            )
            self.window_collector.set_classifier(self.classifier)
            self.window_collector.set_callback(on_window_event)
            self.window_collector.start()

        # Start file collector
        file_config = collector_config.get("file", {})
        if file_config.get("enabled", True):
            self.file_collector = FileCollector()
            self.file_collector.set_classifier(self.classifier)
            self.file_collector.set_callback(on_file_event)

            ignore = config.get("ignore_rules", {})
            self.file_collector.set_ignore_rules(
                ignore.get("dirs", []),
                ignore.get("extensions", []),
            )

            watch_dirs = config.get("watch_dirs", [])
            for d in watch_dirs:
                if os.path.isdir(d):
                    self.file_collector.add_watch_dir(d)

            self.file_collector.start()

        # Start git collector
        git_config = collector_config.get("git", {})
        if git_config.get("enabled", True):
            self.git_collector = GitCollector(
                interval=git_config.get("interval", 300)
            )
            self.git_collector.set_callback(on_git_event)

            # Load known hashes
            try:
                session = get_session()
                hashes = {e.commit_hash for e in session.query(GitEvent.commit_hash).all()}
                self.git_collector.set_known_hashes(hashes)
                session.close()
            except Exception:
                pass

            # Add repos from projects
            try:
                session = get_session()
                projects = session.query(Project).filter(Project.enable_git == 1).all()
                for p in projects:
                    if os.path.isdir(os.path.join(p.path, ".git")):
                        self.git_collector.add_repo(p.path)
                session.close()
            except Exception:
                pass

            self.git_collector.start()

        logger.info("Scheduler started all collectors")

    def stop(self):
        if self.window_collector:
            self.window_collector.flush()
            self.window_collector.stop()
        if self.file_collector:
            self.file_collector.stop()
        if self.git_collector:
            self.git_collector.stop()
        logger.info("Scheduler stopped all collectors")
