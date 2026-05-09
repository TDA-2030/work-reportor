from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from ..storage.database import get_db
from ..storage.models import WindowEvent, FileEvent, GitEvent
from ..utils.time_utils import today_str, week_start_str, week_end_str

router = APIRouter()


def _build_dashboard(db: Session, date_start: str, date_end: str = None):
    if date_end is None:
        date_end = date_start

    # Active time from window events
    active_time = db.query(func.sum(WindowEvent.duration)).filter(
        WindowEvent.start_time >= date_start,
        WindowEvent.start_time < date_end + "T23:59:59"
    ).scalar() or 0

    # Top projects by duration
    top_projects = db.query(
        WindowEvent.project,
        func.sum(WindowEvent.duration).label("duration")
    ).filter(
        WindowEvent.start_time >= date_start,
        WindowEvent.start_time < date_end + "T23:59:59",
        WindowEvent.project.isnot(None),
        WindowEvent.project != ""
    ).group_by(WindowEvent.project).order_by(
        func.sum(WindowEvent.duration).desc()
    ).limit(10).all()

    # Categories
    categories = db.query(
        WindowEvent.category,
        func.sum(WindowEvent.duration).label("duration")
    ).filter(
        WindowEvent.start_time >= date_start,
        WindowEvent.start_time < date_end + "T23:59:59",
        WindowEvent.category.isnot(None)
    ).group_by(WindowEvent.category).all()

    # Recent file events
    recent_files = db.query(FileEvent).filter(
        FileEvent.timestamp >= date_start,
        FileEvent.timestamp < date_end + "T23:59:59"
    ).order_by(FileEvent.timestamp.desc()).limit(10).all()

    # Recent git events
    recent_git = db.query(GitEvent).filter(
        GitEvent.timestamp >= date_start,
        GitEvent.timestamp < date_end + "T23:59:59"
    ).order_by(GitEvent.timestamp.desc()).limit(10).all()

    return {
        "active_time": active_time,
        "top_projects": [
            {"name": p.project or "未分类", "duration": p.duration}
            for p in top_projects
        ],
        "categories": [
            {"name": c.category or "其他", "duration": c.duration}
            for c in categories
        ],
        "recent_files": [
            {
                "event_type": f.event_type,
                "file_path": f.file_path,
                "file_name": f.file_name,
                "project": f.project,
                "timestamp": f.timestamp,
            }
            for f in recent_files
        ],
        "recent_git": [
            {
                "project": g.project,
                "message": g.message,
                "timestamp": g.timestamp,
                "files_changed": g.files_changed,
            }
            for g in recent_git
        ],
    }


@router.get("/today")
def dashboard_today(db: Session = Depends(get_db)):
    today = today_str()
    return _build_dashboard(db, today)


@router.get("/week")
def dashboard_week(db: Session = Depends(get_db)):
    return _build_dashboard(db, week_start_str(), week_end_str())
