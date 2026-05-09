import logging
import threading
import time
from datetime import datetime
from collections import defaultdict
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from ..utils.path_utils import get_file_ext, get_file_name, normalize_path

logger = logging.getLogger(__name__)


class _FileEventHandler(FileSystemEventHandler):
    def __init__(self, collector: "FileCollector"):
        self.collector = collector

    def on_modified(self, event):
        if not event.is_directory:
            self.collector._queue_event("modified", event.src_path)

    def on_created(self, event):
        if not event.is_directory:
            self.collector._queue_event("created", event.src_path)

    def on_deleted(self, event):
        if not event.is_directory:
            self.collector._queue_event("deleted", event.src_path)

    def on_moved(self, event):
        if not event.is_directory:
            self.collector._queue_event("moved", event.dest_path)


class FileCollector:
    def __init__(self):
        self._observer = Observer()
        self._running = False
        self._on_event = None
        self._classifier = None
        self._ignore_dirs = set()
        self._ignore_extensions = set()
        self._event_buffer = defaultdict(float)  # path -> last_event_time
        self._buffer_lock = threading.Lock()
        self._flush_interval = 2  # seconds, dedup window
        self._pending_events = []

    def set_classifier(self, classifier):
        self._classifier = classifier

    def set_callback(self, callback):
        self._on_event = callback

    def set_ignore_rules(self, dirs: list, extensions: list):
        self._ignore_dirs = set(d.lower() for d in dirs)
        self._ignore_extensions = set(e.lower() for e in extensions)

    def add_watch_dir(self, path: str):
        try:
            handler = _FileEventHandler(self)
            self._observer.schedule(handler, path, recursive=True)
            logger.info(f"Watching directory: {path}")
        except Exception as e:
            logger.error(f"Failed to watch {path}: {e}")

    def start(self):
        if self._running:
            return
        self._running = True
        self._observer.start()
        self._flush_thread = threading.Thread(target=self._flush_loop, daemon=True)
        self._flush_thread.start()
        logger.info("File collector started")

    def stop(self):
        self._running = False
        self._observer.stop()
        self._observer.join(timeout=5)
        logger.info("File collector stopped")

    def _should_ignore(self, path: str) -> bool:
        normalized = normalize_path(path).lower()
        for d in self._ignore_dirs:
            if f"/{d}/" in normalized or normalized.endswith(f"/{d}"):
                return True
        ext = get_file_ext(path)
        if ext in self._ignore_extensions:
            return True
        return False

    def _queue_event(self, event_type: str, path: str):
        if self._should_ignore(path):
            return

        now = time.time()
        key = f"{event_type}:{path}"

        with self._buffer_lock:
            last = self._event_buffer.get(key, 0)
            if now - last < self._flush_interval:
                return  # dedup
            self._event_buffer[key] = now

            self._pending_events.append({
                "event_type": event_type,
                "file_path": normalize_path(path),
                "file_name": get_file_name(path),
                "file_ext": get_file_ext(path),
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            })

    def _flush_loop(self):
        while self._running:
            time.sleep(self._flush_interval)
            self._flush()

    def _flush(self):
        with self._buffer_lock:
            events = self._pending_events[:]
            self._pending_events.clear()

        for event in events:
            # Classify
            if self._classifier:
                event["project"] = self._classifier.detect_project_from_path(
                    event["file_path"]
                )
                event["category"] = self._classifier.classify_file(event["file_ext"])
            else:
                event["project"] = ""
                event["category"] = ""

            if self._on_event:
                self._on_event(event)
