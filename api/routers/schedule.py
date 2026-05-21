"""
Scheduled task API endpoints
"""

import json
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from fastapi import APIRouter, HTTPException
from loguru import logger

from api.schemas.schedule import (
    ScheduleConfig,
    ScheduleTime,
    ScheduleListResponse,
    ScheduleCreateRequest,
    ScheduleUpdateRequest,
)

router = APIRouter(prefix="/schedule", tags=["Scheduled Tasks"])


def _storage_path() -> Path:
    from api.config import api_config
    p = Path(api_config.data_dir) / "schedules.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    return p


def _load_raw() -> list[dict]:
    """Load schedules as raw dicts (preserves template_data)."""
    try:
        sp = _storage_path()
        if not sp.exists():
            return []
        with open(sp, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def _save_raw(schedules: list[dict]):
    sp = _storage_path()
    with open(sp, "w", encoding="utf-8") as f:
        json.dump(schedules, f, ensure_ascii=False, indent=2)


def _raw_to_model(raw: dict) -> ScheduleConfig:
    """Convert raw dict to ScheduleConfig, dropping extra keys like template_data."""
    model_fields = {k: v for k, v in raw.items() if k != "template_data"}
    return ScheduleConfig(**model_fields)


def _calc_next_run(st: ScheduleTime) -> str:
    now = datetime.now()
    candidates = []
    for wd in st.weekdays:
        days_ahead = (wd - now.weekday()) % 7
        if days_ahead == 0:
            candidate = now.replace(hour=st.hour, minute=st.minute, second=0, microsecond=0)
            if candidate <= now:
                candidate += timedelta(days=7)
        else:
            candidate = now.replace(hour=st.hour, minute=st.minute, second=0, microsecond=0) + timedelta(days=days_ahead)
        candidates.append(candidate)
    if not candidates:
        return (now + timedelta(days=1)).replace(hour=st.hour, minute=st.minute, second=0, microsecond=0).isoformat()
    return min(candidates).isoformat()


@router.get("/list", response_model=ScheduleListResponse)
async def list_schedules():
    raw = _load_raw()
    models = [_raw_to_model(r) for r in raw]
    return ScheduleListResponse(schedules=models)


@router.post("/create", response_model=ScheduleConfig)
async def create_schedule(req: ScheduleCreateRequest):
    raw = _load_raw()
    cfg = ScheduleConfig(
        id=str(uuid.uuid4()),
        name=req.name,
        enabled=True,
        schedule_time=req.schedule_time,
        template_id=req.template_id,
        created_at=datetime.now().isoformat(),
        next_run_at=_calc_next_run(req.schedule_time),
    )
    entry = cfg.model_dump()
    if req.template_data:
        entry["template_data"] = req.template_data
    raw.append(entry)
    _save_raw(raw)
    logger.info(f"Created schedule: {cfg.name} ({cfg.id})")
    return cfg


@router.put("/{schedule_id}", response_model=ScheduleConfig)
async def update_schedule(schedule_id: str, req: ScheduleUpdateRequest):
    raw = _load_raw()
    for entry in raw:
        if entry.get("id") == schedule_id:
            if req.name is not None:
                entry["name"] = req.name
            if req.enabled is not None:
                entry["enabled"] = req.enabled
            if req.schedule_time is not None:
                entry["schedule_time"] = req.schedule_time.model_dump()
                entry["next_run_at"] = _calc_next_run(req.schedule_time)
            if req.template_id is not None:
                entry["template_id"] = req.template_id
            _save_raw(raw)
            return _raw_to_model(entry)
    raise HTTPException(status_code=404, detail="Schedule not found")


@router.delete("/{schedule_id}")
async def delete_schedule(schedule_id: str):
    raw = _load_raw()
    raw = [r for r in raw if r.get("id") != schedule_id]
    _save_raw(raw)
    return {"success": True}
