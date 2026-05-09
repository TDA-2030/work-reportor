import json
import yaml
import os
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Optional

from ..storage.database import get_db
from ..storage.models import Setting, IgnoreRule

router = APIRouter()

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "config.yaml")


class SettingUpdate(BaseModel):
    key: str
    value: str


class WatchDirCreate(BaseModel):
    path: str


class IgnoreRuleCreate(BaseModel):
    rule_type: str  # "dir", "extension", "keyword"
    pattern: str


class AISettingsUpdate(BaseModel):
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    model: Optional[str] = None
    language: Optional[str] = None
    style: Optional[str] = None


def _load_config() -> dict:
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    return {}


def _save_config(config: dict):
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        yaml.dump(config, f, allow_unicode=True, default_flow_style=False)


@router.get("")
def get_settings(db: Session = Depends(get_db)):
    config = _load_config()
    ignore_rules = db.query(IgnoreRule).all()
    return {
        "config": config,
        "ignore_rules": [
            {
                "id": r.id,
                "rule_type": r.rule_type,
                "pattern": r.pattern,
                "enabled": bool(r.enabled),
            }
            for r in ignore_rules
        ],
    }


@router.put("")
def update_settings(data: dict, db: Session = Depends(get_db)):
    config = _load_config()
    # Deep merge
    for key, value in data.items():
        if isinstance(value, dict) and key in config and isinstance(config[key], dict):
            config[key].update(value)
        else:
            config[key] = value
    _save_config(config)
    return {"ok": True}


@router.post("/watch-dirs")
def add_watch_dir(data: WatchDirCreate):
    config = _load_config()
    watch_dirs = config.get("watch_dirs", [])
    if data.path not in watch_dirs:
        watch_dirs.append(data.path)
        config["watch_dirs"] = watch_dirs
        _save_config(config)
    return {"ok": True, "watch_dirs": config["watch_dirs"]}


@router.delete("/watch-dirs")
def remove_watch_dir(path: str):
    config = _load_config()
    watch_dirs = config.get("watch_dirs", [])
    if path in watch_dirs:
        watch_dirs.remove(path)
        config["watch_dirs"] = watch_dirs
        _save_config(config)
    return {"ok": True, "watch_dirs": config["watch_dirs"]}


@router.post("/ignore-rules")
def add_ignore_rule(data: IgnoreRuleCreate, db: Session = Depends(get_db)):
    rule = IgnoreRule(rule_type=data.rule_type, pattern=data.pattern, enabled=1)
    db.add(rule)
    db.commit()
    return {"id": rule.id, "rule_type": rule.rule_type, "pattern": rule.pattern}


@router.delete("/ignore-rules/{rule_id}")
def delete_ignore_rule(rule_id: int, db: Session = Depends(get_db)):
    rule = db.query(IgnoreRule).get(rule_id)
    if not rule:
        raise HTTPException(status_code=404, detail="规则不存在")
    db.delete(rule)
    db.commit()
    return {"ok": True}


@router.put("/ai")
def update_ai_settings(data: AISettingsUpdate):
    config = _load_config()
    ai = config.get("ai", {})
    if data.api_key is not None:
        ai["api_key"] = data.api_key
    if data.base_url is not None:
        ai["base_url"] = data.base_url
    if data.model is not None:
        ai["model"] = data.model
    if data.language is not None:
        ai["language"] = data.language
    if data.style is not None:
        ai["style"] = data.style
    config["ai"] = ai
    _save_config(config)
    return {"ok": True}
