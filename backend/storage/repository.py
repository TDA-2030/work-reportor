from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from .models import WindowEvent, FileEvent, GitEvent, Project, Setting, IgnoreRule


class WindowEventRepo:
    def __init__(self, db: Session):
        self.db = db

    def add(self, event: WindowEvent):
        self.db.add(event)
        self.db.commit()
        return event

    def get_by_date(self, date: str):
        return self.db.query(WindowEvent).filter(
            WindowEvent.start_time.like(f"{date}%")
        ).order_by(WindowEvent.start_time).all()

    def get_by_range(self, start: str, end: str):
        return self.db.query(WindowEvent).filter(
            and_(WindowEvent.start_time >= start, WindowEvent.start_time <= end)
        ).order_by(WindowEvent.start_time).all()

    def get_latest(self):
        return self.db.query(WindowEvent).order_by(
            WindowEvent.start_time.desc()
        ).first()

    def update_end_time(self, event_id: int, end_time: str, duration: int):
        event = self.db.query(WindowEvent).get(event_id)
        if event:
            event.end_time = end_time
            event.duration = duration
            self.db.commit()


class FileEventRepo:
    def __init__(self, db: Session):
        self.db = db

    def add(self, event: FileEvent):
        self.db.add(event)
        self.db.commit()
        return event

    def get_by_date(self, date: str):
        return self.db.query(FileEvent).filter(
            FileEvent.timestamp.like(f"{date}%")
        ).order_by(FileEvent.timestamp.desc()).all()

    def get_by_range(self, start: str, end: str):
        return self.db.query(FileEvent).filter(
            and_(FileEvent.timestamp >= start, FileEvent.timestamp <= end)
        ).order_by(FileEvent.timestamp.desc()).all()

    def get_recent(self, limit: int = 20):
        return self.db.query(FileEvent).order_by(
            FileEvent.timestamp.desc()
        ).limit(limit).all()


class GitEventRepo:
    def __init__(self, db: Session):
        self.db = db

    def add(self, event: GitEvent):
        existing = self.db.query(GitEvent).filter(
            GitEvent.commit_hash == event.commit_hash
        ).first()
        if existing:
            return existing
        self.db.add(event)
        self.db.commit()
        return event

    def get_by_date(self, date: str):
        return self.db.query(GitEvent).filter(
            GitEvent.timestamp.like(f"{date}%")
        ).order_by(GitEvent.timestamp.desc()).all()

    def get_by_range(self, start: str, end: str):
        return self.db.query(GitEvent).filter(
            and_(GitEvent.timestamp >= start, GitEvent.timestamp <= end)
        ).order_by(GitEvent.timestamp.desc()).all()

    def get_recent(self, limit: int = 20):
        return self.db.query(GitEvent).order_by(
            GitEvent.timestamp.desc()
        ).limit(limit).all()

    def exists(self, commit_hash: str) -> bool:
        return self.db.query(GitEvent).filter(
            GitEvent.commit_hash == commit_hash
        ).first() is not None


class ProjectRepo:
    def __init__(self, db: Session):
        self.db = db

    def add(self, project: Project):
        self.db.add(project)
        self.db.commit()
        return project

    def get_all(self):
        return self.db.query(Project).all()

    def get_by_name(self, name: str) -> Optional[Project]:
        return self.db.query(Project).filter(Project.name == name).first()

    def update(self, name: str, **kwargs):
        project = self.get_by_name(name)
        if project:
            for k, v in kwargs.items():
                setattr(project, k, v)
            self.db.commit()
        return project

    def delete(self, name: str):
        project = self.get_by_name(name)
        if project:
            self.db.delete(project)
            self.db.commit()
            return True
        return False


class SettingRepo:
    def __init__(self, db: Session):
        self.db = db

    def get(self, key: str, default: str = "") -> str:
        setting = self.db.query(Setting).filter(Setting.key == key).first()
        return setting.value if setting else default

    def set(self, key: str, value: str):
        setting = self.db.query(Setting).filter(Setting.key == key).first()
        if setting:
            setting.value = value
        else:
            self.db.add(Setting(key=key, value=value))
        self.db.commit()

    def get_all(self) -> dict:
        settings = self.db.query(Setting).all()
        return {s.key: s.value for s in settings}


class IgnoreRuleRepo:
    def __init__(self, db: Session):
        self.db = db

    def add(self, rule_type: str, pattern: str):
        rule = IgnoreRule(rule_type=rule_type, pattern=pattern, enabled=1)
        self.db.add(rule)
        self.db.commit()
        return rule

    def get_all(self):
        return self.db.query(IgnoreRule).all()

    def get_enabled(self):
        return self.db.query(IgnoreRule).filter(IgnoreRule.enabled == 1).all()

    def delete(self, rule_id: int):
        rule = self.db.query(IgnoreRule).get(rule_id)
        if rule:
            self.db.delete(rule)
            self.db.commit()
            return True
        return False

    def toggle(self, rule_id: int, enabled: bool):
        rule = self.db.query(IgnoreRule).get(rule_id)
        if rule:
            rule.enabled = 1 if enabled else 0
            self.db.commit()
        return rule
