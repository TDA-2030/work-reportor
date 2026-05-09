import json
import os
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional

from ..storage.database import get_db
from ..storage.models import WindowEvent, FileEvent, GitEvent
from ..utils.time_utils import format_duration

router = APIRouter()

REPORTS_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "reports")


class ReportRequest(BaseModel):
    report_type: str = "daily"  # daily / weekly
    start_date: str = ""
    end_date: str = ""
    style: str = "formal"


class AIReportRequest(BaseModel):
    report_type: str = "weekly"
    start_date: str = ""
    end_date: str = ""
    style: str = "formal"
    summary_data: Optional[dict] = None


def _aggregate_data(db: Session, start: str, end: str) -> dict:
    end_ts = end + "T23:59:59"

    # Project durations
    projects_raw = db.query(
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
        FileEvent.project.isnot(None),
    ).group_by(FileEvent.project).all()
    file_map = {f.project: f.count for f in file_counts}

    # Main files per project
    main_files_raw = db.query(
        FileEvent.project,
        FileEvent.file_name,
        func.count(FileEvent.id).label("count"),
    ).filter(
        FileEvent.timestamp >= start,
        FileEvent.timestamp <= end_ts,
        FileEvent.project.isnot(None),
    ).group_by(FileEvent.project, FileEvent.file_name).order_by(
        func.count(FileEvent.id).desc()
    ).all()

    main_files_map: dict[str, list] = {}
    for row in main_files_raw:
        files = main_files_map.setdefault(row.project, [])
        if len(files) < 5:
            files.append(row.file_name)

    # Git commits per project
    git_raw = db.query(GitEvent).filter(
        GitEvent.timestamp >= start,
        GitEvent.timestamp <= end_ts,
    ).order_by(GitEvent.timestamp.desc()).all()

    git_map: dict[str, list] = {}
    for g in git_raw:
        commits = git_map.setdefault(g.project, [])
        commits.append(g.message)

    # Categories
    categories = db.query(
        WindowEvent.category,
        func.sum(WindowEvent.duration).label("duration"),
    ).filter(
        WindowEvent.start_time >= start,
        WindowEvent.start_time <= end_ts,
        WindowEvent.category.isnot(None),
    ).group_by(WindowEvent.category).all()

    projects = []
    for p in projects_raw:
        name = p.project
        projects.append({
            "name": name,
            "active_time": format_duration(p.duration),
            "file_changes": file_map.get(name, 0),
            "main_files": main_files_map.get(name, []),
            "commits": git_map.get(name, []),
        })

    return {
        "range": f"{start} ~ {end}",
        "projects": projects,
        "categories": {
            (c.category or "其他"): format_duration(c.duration)
            for c in categories
        },
    }


def _generate_markdown(data: dict, report_type: str, style: str) -> str:
    lines = []
    type_label = "日报" if report_type == "daily" else "周报"
    lines.append(f"# 工作{type_label}")
    lines.append(f"\n**时间范围**: {data['range']}\n")

    if data["projects"]:
        lines.append("## 项目概览\n")
        for p in data["projects"]:
            lines.append(f"### {p['name']}")
            lines.append(f"- 活跃时间: {p['active_time']}")
            lines.append(f"- 文件修改: {p['file_changes']} 次")
            if p["main_files"]:
                lines.append(f"- 主要文件: {', '.join(p['main_files'])}")
            if p["commits"]:
                lines.append("- Git 提交:")
                for c in p["commits"]:
                    lines.append(f"  - {c}")
            lines.append("")

    if data["categories"]:
        lines.append("## 工作类型分布\n")
        for cat, dur in data["categories"].items():
            lines.append(f"- {cat}: {dur}")
        lines.append("")

    return "\n".join(lines)


@router.post("/preview")
def preview_report(req: ReportRequest, db: Session = Depends(get_db)):
    data = _aggregate_data(db, req.start_date, req.end_date)
    return data


@router.post("/generate")
def generate_report(req: ReportRequest, db: Session = Depends(get_db)):
    data = _aggregate_data(db, req.start_date, req.end_date)
    markdown = _generate_markdown(data, req.report_type, req.style)

    # Save to file
    sub_dir = "daily" if req.report_type == "daily" else "weekly"
    save_dir = os.path.join(REPORTS_DIR, sub_dir)
    os.makedirs(save_dir, exist_ok=True)
    filename = f"{req.start_date}_{req.end_date}.md"
    filepath = os.path.join(save_dir, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(markdown)

    return {"markdown": markdown, "file": filepath, "data": data}


@router.post("/generate-ai")
async def generate_ai_report(req: AIReportRequest, db: Session = Depends(get_db)):
    import yaml

    config_path = os.path.join(os.path.dirname(__file__), "..", "..", "config.yaml")
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f) or {}

    ai_config = config.get("ai", {})
    api_key = ai_config.get("api_key", "")
    if not api_key:
        raise HTTPException(status_code=400, detail="请先在设置中配置 AI API Key")

    data = req.summary_data or _aggregate_data(db, req.start_date, req.end_date)

    prompt = f"""你是一个工作周报助手。请根据下面的结构化工作记录，生成一份简洁、正式、适合提交给领导的中文周报。

要求：
1. 不要编造没有出现的信息
2. 按项目归纳
3. 输出包括：本周工作内容、问题与优化、下周计划
4. 语气正式，不要空洞
5. 如果数据不足，请保守总结

工作记录：
{json.dumps(data, ensure_ascii=False, indent=2)}"""

    from openai import OpenAI

    client = OpenAI(
        api_key=api_key,
        base_url=ai_config.get("base_url") or None,
    )
    response = client.chat.completions.create(
        model=ai_config.get("model", "gpt-4o-mini"),
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
    )
    ai_text = response.choices[0].message.content

    # Save
    sub_dir = "daily" if req.report_type == "daily" else "weekly"
    save_dir = os.path.join(REPORTS_DIR, sub_dir)
    os.makedirs(save_dir, exist_ok=True)
    filename = f"{req.start_date}_{req.end_date}_ai.md"
    filepath = os.path.join(save_dir, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(ai_text)

    return {"markdown": ai_text, "file": filepath, "data": data}


@router.get("/list")
def list_reports():
    result = []
    for sub in ["daily", "weekly"]:
        d = os.path.join(REPORTS_DIR, sub)
        if not os.path.isdir(d):
            continue
        for fname in sorted(os.listdir(d), reverse=True):
            if fname.endswith(".md"):
                result.append({
                    "type": sub,
                    "filename": fname,
                    "path": os.path.join(d, fname),
                })
    return result


@router.get("/{report_type}/{filename}")
def get_report(report_type: str, filename: str):
    filepath = os.path.join(REPORTS_DIR, report_type, filename)
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="报告不存在")
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    return {"content": content, "filename": filename}
