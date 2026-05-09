from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import func

from ..storage.database import get_db
from ..storage.models import Project, WindowEvent, FileEvent, GitEvent
from ..utils.time_utils import now_str, week_start_str, week_end_str

router = APIRouter()


class ProjectCreate(BaseModel):
    name: str
    path: str
    type: str = ""
    enable_git: bool = True


class ProjectUpdate(BaseModel):
    path: str = None
    type: str = None
    enable_git: bool = None


@router.get("")
def list_projects(db: Session = Depends(get_db)):
    projects = db.query(Project).all()
    return [
        {
            "id": p.id,
            "name": p.name,
            "path": p.path,
            "type": p.type,
            "enable_git": bool(p.enable_git),
            "created_at": p.created_at,
        }
        for p in projects
    ]


@router.post("")
def create_project(data: ProjectCreate, db: Session = Depends(get_db)):
    existing = db.query(Project).filter(Project.name == data.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="项目名已存在")
    project = Project(
        name=data.name,
        path=data.path,
        type=data.type,
        enable_git=1 if data.enable_git else 0,
        created_at=now_str(),
    )
    db.add(project)
    db.commit()
    return {"id": project.id, "name": project.name}


@router.get("/{project_name}/stats")
def project_stats(project_name: str, db: Session = Depends(get_db)):
    start = week_start_str()
    end = week_end_str() + "T23:59:59"

    active_time = db.query(func.sum(WindowEvent.duration)).filter(
        WindowEvent.project == project_name,
        WindowEvent.start_time >= start,
        WindowEvent.start_time <= end,
    ).scalar() or 0

    file_changes = db.query(func.count(FileEvent.id)).filter(
        FileEvent.project == project_name,
        FileEvent.timestamp >= start,
        FileEvent.timestamp <= end,
    ).scalar() or 0

    git_commits = db.query(func.count(GitEvent.id)).filter(
        GitEvent.project == project_name,
        GitEvent.timestamp >= start,
        GitEvent.timestamp <= end,
    ).scalar() or 0

    return {
        "project": project_name,
        "active_time": active_time,
        "file_changes": file_changes,
        "git_commits": git_commits,
    }


@router.put("/{project_name}")
def update_project(
    project_name: str, data: ProjectUpdate, db: Session = Depends(get_db)
):
    project = db.query(Project).filter(Project.name == project_name).first()
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    if data.path is not None:
        project.path = data.path
    if data.type is not None:
        project.type = data.type
    if data.enable_git is not None:
        project.enable_git = 1 if data.enable_git else 0
    db.commit()
    return {"ok": True}


@router.delete("/{project_name}")
def delete_project(project_name: str, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.name == project_name).first()
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")
    db.delete(project)
    db.commit()
    return {"ok": True}
