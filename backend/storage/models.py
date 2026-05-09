from sqlalchemy import Column, Integer, Text, create_engine
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class WindowEvent(Base):
    __tablename__ = "window_events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    app_name = Column(Text)
    process_name = Column(Text)
    window_title = Column(Text)
    category = Column(Text)
    project = Column(Text)
    start_time = Column(Text)
    end_time = Column(Text)
    duration = Column(Integer)


class FileEvent(Base):
    __tablename__ = "file_events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    event_type = Column(Text)
    file_path = Column(Text)
    file_name = Column(Text)
    file_ext = Column(Text)
    project = Column(Text)
    category = Column(Text)
    timestamp = Column(Text)


class GitEvent(Base):
    __tablename__ = "git_events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    project = Column(Text)
    repo_path = Column(Text)
    commit_hash = Column(Text, unique=True)
    message = Column(Text)
    timestamp = Column(Text)
    files_changed = Column(Integer)
    insertions = Column(Integer)
    deletions = Column(Integer)


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(Text, unique=True)
    path = Column(Text)
    type = Column(Text)
    enable_git = Column(Integer, default=1)
    created_at = Column(Text)


class Setting(Base):
    __tablename__ = "settings"

    key = Column(Text, primary_key=True)
    value = Column(Text)


class IgnoreRule(Base):
    __tablename__ = "ignore_rules"

    id = Column(Integer, primary_key=True, autoincrement=True)
    rule_type = Column(Text)
    pattern = Column(Text)
    enabled = Column(Integer, default=1)
