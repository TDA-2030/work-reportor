from sqlalchemy.orm import Session
from sqlalchemy import func
from ..storage.models import WindowEvent, FileEvent, GitEvent
from ..utils.time_utils import format_duration


def aggregate_period(db: Session, start: str, end: str) -> dict:
    """Aggregate work data for a time period."""
    end_ts = end + "T23:59:59"

    # Total active time
    total_time = db.query(func.sum(WindowEvent.duration)).filter(
        WindowEvent.start_time >= start,
        WindowEvent.start_time <= end_ts,
    ).scalar() or 0

    # Per-project stats
    project_times = db.query(
        WindowEvent.project,
        func.sum(WindowEvent.duration).label("duration"),
    ).filter(
        WindowEvent.start_time >= start,
        WindowEvent.start_time <= end_ts,
        WindowEvent.project.isnot(None),
        WindowEvent.project != "",
    ).group_by(WindowEvent.project).order_by(
        func.sum(WindowEvent.duration).desc()
    ).all()

    # File changes per project
    file_counts = db.query(
        FileEvent.project,
        func.count(FileEvent.id).label("count"),
    ).filter(
        FileEvent.timestamp >= start,
        FileEvent.timestamp <= end_ts,
    ).group_by(FileEvent.project).all()
    fc_map = {f.project: f.count for f in file_counts}

    # Git commits per project
    git_commits = db.query(GitEvent).filter(
        GitEvent.timestamp >= start,
        GitEvent.timestamp <= end_ts,
    ).order_by(GitEvent.timestamp.desc()).all()

    gc_map: dict[str, list] = {}
    for g in git_commits:
        gc_map.setdefault(g.project, []).append(g.message)

    # Category distribution
    categories = db.query(
        WindowEvent.category,
        func.sum(WindowEvent.duration).label("duration"),
    ).filter(
        WindowEvent.start_time >= start,
        WindowEvent.start_time <= end_ts,
        WindowEvent.category.isnot(None),
    ).group_by(WindowEvent.category).all()

    projects = []
    for pt in project_times:
        projects.append({
            "name": pt.project,
            "active_time": format_duration(pt.duration),
            "active_seconds": pt.duration,
            "file_changes": fc_map.get(pt.project, 0),
            "commits": gc_map.get(pt.project, []),
        })

    return {
        "range": f"{start} ~ {end}",
        "total_active_time": format_duration(total_time),
        "total_seconds": total_time,
        "projects": projects,
        "categories": {
            (c.category or "其他"): format_duration(c.duration)
            for c in categories
        },
    }
