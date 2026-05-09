import threading
import time
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


def _get_active_window_info() -> dict:
    """Get current foreground window info (Windows only)."""
    try:
        import win32gui
        import win32process
        import psutil

        hwnd = win32gui.GetForegroundWindow()
        if not hwnd:
            return None

        window_title = win32gui.GetWindowText(hwnd)
        if not window_title:
            return None

        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        try:
            process = psutil.Process(pid)
            process_name = process.name()
            app_name = process_name.replace(".exe", "")
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            process_name = ""
            app_name = ""

        return {
            "app_name": app_name,
            "process_name": process_name,
            "window_title": window_title,
        }
    except Exception as e:
        logger.debug(f"Failed to get window info: {e}")
        return None


class WindowCollector:
    def __init__(self, interval: int = 3):
        self.interval = interval
        self._running = False
        self._thread = None
        self._current_event = None
        self._on_event = None  # callback(event_dict)
        self._classifier = None

    def set_classifier(self, classifier):
        self._classifier = classifier

    def set_callback(self, callback):
        self._on_event = callback

    def start(self):
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()
        logger.info("Window collector started")

    def stop(self):
        self._running = False
        if self._thread:
            self._thread.join(timeout=5)
        logger.info("Window collector stopped")

    def _run(self):
        while self._running:
            try:
                info = _get_active_window_info()
                if info:
                    self._process_window(info)
            except Exception as e:
                logger.error(f"Window collector error: {e}")
            time.sleep(self.interval)

    def _process_window(self, info: dict):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Check if same window as current
        if self._current_event and self._is_same_window(info):
            self._current_event["end_time"] = now
            start = datetime.strptime(self._current_event["start_time"], "%Y-%m-%d %H:%M:%S")
            end = datetime.strptime(now, "%Y-%m-%d %H:%M:%S")
            self._current_event["duration"] = int((end - start).total_seconds())
            return

        # Finalize previous event
        if self._current_event and self._on_event:
            self._on_event(self._current_event)

        # Classify
        category = ""
        project = ""
        if self._classifier:
            category = self._classifier.classify_app(info["app_name"], info["window_title"])
            project = self._classifier.detect_project(info["window_title"])

        self._current_event = {
            "app_name": info["app_name"],
            "process_name": info["process_name"],
            "window_title": info["window_title"],
            "category": category,
            "project": project,
            "start_time": now,
            "end_time": now,
            "duration": 0,
        }

    def _is_same_window(self, info: dict) -> bool:
        if not self._current_event:
            return False
        return (
            self._current_event["app_name"] == info["app_name"]
            and self._current_event["window_title"] == info["window_title"]
        )

    def flush(self):
        """Flush current event."""
        if self._current_event and self._on_event:
            self._on_event(self._current_event)
            self._current_event = None
