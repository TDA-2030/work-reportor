from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from ..storage.database import get_db
from ..storage.models import WindowEvent, FileEvent, GitEvent
from ..utils.time_utils import today_str

router = APIRouter()


@router.get("/timeline")
def get_timeline(
    date: str = Query(default=None),
    project: str = Query(default=None),
    category: str = Query(default=None),
    db: Session = Depends(get_db),
):
    if date is None:
        date = today_str()

    query = db.query(WindowEvent).filter(
        WindowEvent.start_time.like(f"{date}%")
    )
    if project:
        query = query.filter(WindowEvent.project == project)
    if category:
        query = query.filter(WindowEvent.category == category)

    events = query.order_by(WindowEvent.start_time).all()
    return [
        {
            "id": e.id,
            "app_name": e.app_name,
            "process_name": e.process_name,
            "window_title": e.window_title,
            "category": e.category,
            "project": e.project,
            "start_time": e.start_time,
            "end_time": e.end_time,
            "duration": e.duration,
        }
        for e in events
    ]


@router.get("/files")
def get_files(
    date: str = Query(default=None),
    project: str = Query(default=None),
    file_ext: str = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    if date is None:
        date = today_str()

    query = db.query(FileEvent).filter(
        FileEvent.timestamp.like(f"{date}%")
    )
    if project:
        query = query.filter(FileEvent.project == project)
    if file_ext:
        query = query.filter(FileEvent.file_ext == file_ext)

    total = query.count()
    events = query.order_by(FileEvent.timestamp.desc()).offset(
        (page - 1) * page_size
    ).limit(page_size).all()

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": [
            {
                "id": e.id,
                "event_type": e.event_type,
                "file_path": e.file_path,
                "file_name": e.file_name,
                "file_ext": e.file_ext,
                "project": e.project,
                "category": e.category,
                "timestamp": e.timestamp,
            }
            for e in events
        ],
    }


@router.get("/windows")
def get_windows(
    date: str = Query(default=None),
    db: Session = Depends(get_db),
):
    if date is None:
        date = today_str()

    events = db.query(WindowEvent).filter(
        WindowEvent.start_time.like(f"{date}%")
    ).order_by(WindowEvent.start_time).all()

    return [
        {
            "id": e.id,
            "app_name": e.app_name,
            "process_name": e.process_name,
            "window_title": e.window_title,
            "category": e.category,
            "project": e.project,
            "start_time": e.start_time,
            "end_time": e.end_time,
            "duration": e.duration,
        }
        for e in events
    ]


@router.get("/git")
def get_git(
    start_date: str = Query(default=None),
    end_date: str = Query(default=None),
    project: str = Query(default=None),
    db: Session = Depends(get_db),
):
    if start_date is None:
        start_date = today_str()
    if end_date is None:
        end_date = start_date

    query = db.query(GitEvent).filter(
        GitEvent.timestamp >= start_date,
        GitEvent.timestamp <= end_date + "T23:59:59",
    )
    if project:
        query = query.filter(GitEvent.project == project)

    events = query.order_by(GitEvent.timestamp.desc()).all()
    return [
        {
            "id": e.id,
            "project": e.project,
            "repo_path": e.repo_path,
            "commit_hash": e.commit_hash,
            "message": e.message,
            "timestamp": e.timestamp,
            "files_changed": e.files_changed,
            "insertions": e.insertions,
            "deletions": e.deletions,
        }
        for e in events
    ]
