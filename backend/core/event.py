import asyncio
import logging
from ..storage.database import get_session
from ..storage.models import WindowEvent, FileEvent, GitEvent
from ..api.websocket_api import manager

logger = logging.getLogger(__name__)

_loop = None


def set_event_loop(loop):
    global _loop
    _loop = loop


def on_window_event(event: dict):
    """Called by window collector when a window event is finalized."""
    if event.get("duration", 0) < 3:
        return  # Skip very short events

    try:
        session = get_session()
        db_event = WindowEvent(
            app_name=event["app_name"],
            process_name=event["process_name"],
            window_title=event["window_title"],
            category=event.get("category", ""),
            project=event.get("project", ""),
            start_time=event["start_time"],
            end_time=event["end_time"],
            duration=event.get("duration", 0),
        )
        session.add(db_event)
        session.commit()
        session.close()

        _broadcast({
            "type": "window_event",
            "app_name": event["app_name"],
            "window_title": event["window_title"],
            "project": event.get("project", ""),
            "category": event.get("category", ""),
            "timestamp": event["start_time"],
        })
    except Exception as e:
        logger.error(f"Failed to save window event: {e}")


def on_file_event(event: dict):
    """Called by file collector when a file event occurs."""
    try:
        session = get_session()
        db_event = FileEvent(
            event_type=event["event_type"],
            file_path=event["file_path"],
            file_name=event["file_name"],
            file_ext=event["file_ext"],
            project=event.get("project", ""),
            category=event.get("category", ""),
            timestamp=event["timestamp"],
        )
        session.add(db_event)
        session.commit()
        session.close()

        _broadcast({
            "type": "file_event",
            "event_type": event["event_type"],
            "file_path": event["file_path"],
            "project": event.get("project", ""),
            "timestamp": event["timestamp"],
        })
    except Exception as e:
        logger.error(f"Failed to save file event: {e}")


def on_git_event(event: dict):
    """Called by git collector when a new commit is found."""
    try:
        session = get_session()
        # Check if already exists
        existing = session.query(GitEvent).filter(
            GitEvent.commit_hash == event["commit_hash"]
        ).first()
        if existing:
            session.close()
            return

        db_event = GitEvent(
            project=event["project"],
            repo_path=event["repo_path"],
            commit_hash=event["commit_hash"],
            message=event["message"],
            timestamp=event["timestamp"],
            files_changed=event.get("files_changed", 0),
            insertions=event.get("insertions", 0),
            deletions=event.get("deletions", 0),
        )
        session.add(db_event)
        session.commit()
        session.close()

        _broadcast({
            "type": "git_event",
            "project": event["project"],
            "message": event["message"],
            "timestamp": event["timestamp"],
        })
    except Exception as e:
        logger.error(f"Failed to save git event: {e}")


def _broadcast(data: dict):
    if _loop and _loop.is_running():
        asyncio.run_coroutine_threadsafe(manager.broadcast(data), _loop)
