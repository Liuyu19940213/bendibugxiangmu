"""
Schedule executor - background task that polls for due schedules and triggers batch runs.

Runs as an asyncio background task, checking every 30 seconds.
Registered in api/app.py lifespan startup.
"""

import json
import asyncio
from datetime import datetime, timedelta
from pathlib import Path
from loguru import logger

from api.config import api_config
from api.schemas.schedule import ScheduleConfig, ScheduleTime
from api.batch_manager import batch_manager
from api.schemas.batch import BatchRunRequest, BatchModuleRequest, GlobalConfig


def _schedules_path() -> Path:
    p = Path(api_config.data_dir) / "schedules.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    return p


def _load_schedules() -> list[dict]:
    sp = _schedules_path()
    if not sp.exists():
        return []
    try:
        with open(sp, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load schedules: {e}")
        return []


def _save_schedules(schedules: list[dict]):
    sp = _schedules_path()
    with open(sp, "w", encoding="utf-8") as f:
        json.dump(schedules, f, ensure_ascii=False, indent=2)


def _calc_next_run(st_dict: dict) -> str:
    """Calculate next run time from schedule_time dict"""
    now = datetime.now()
    hour = st_dict.get("hour", 8)
    minute = st_dict.get("minute", 0)
    weekdays = st_dict.get("weekdays", [0, 1, 2, 3, 4, 5, 6])

    candidates = []
    for wd in weekdays:
        days_ahead = (wd - now.weekday()) % 7
        candidate = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        if days_ahead == 0:
            if candidate <= now:
                candidate += timedelta(days=7)
        else:
            candidate += timedelta(days=days_ahead)
        candidates.append(candidate)

    if not candidates:
        # Fallback: tomorrow same time
        return (now.replace(hour=hour, minute=minute, second=0, microsecond=0) + timedelta(days=1)).isoformat()

    return min(candidates).isoformat()


async def schedule_loop():
    """
    Background loop that polls schedules and triggers due batches.

    Checks every 30 seconds. On startup, waits 10 seconds for other services to initialize.
    """
    await asyncio.sleep(10)  # Let other services initialize first
    logger.info("📅 Schedule poller started (interval: 30s)")

    while True:
        try:
            schedules = _load_schedules()
            now = datetime.now()
            modified = False

            for s in schedules:
                if not s.get("enabled", True):
                    continue

                next_run_str = s.get("next_run_at")
                if not next_run_str:
                    # First time: calculate next run
                    st = s.get("schedule_time", {})
                    s["next_run_at"] = _calc_next_run(st)
                    modified = True
                    continue

                try:
                    next_run = datetime.fromisoformat(next_run_str)
                except (ValueError, TypeError):
                    st = s.get("schedule_time", {})
                    s["next_run_at"] = _calc_next_run(st)
                    modified = True
                    continue

                if now >= next_run:
                    logger.info(f"⏰ Schedule triggered: {s.get('name', s.get('id', '?'))}")

                    # Try to execute
                    template_data = s.get("template_data")
                    if template_data:
                        try:
                            modules_raw = template_data.get("modules", [])
                            global_config_raw = template_data.get("global_config", {})

                            modules = [BatchModuleRequest(**m) for m in modules_raw if m.get("enabled", True)]
                            if modules:
                                global_config = GlobalConfig(**global_config_raw)
                                batch_id = batch_manager.create_batch(modules, global_config)
                                await batch_manager.start_batch(batch_id)
                                logger.info(f"  → Batch {batch_id} started ({len(modules)} modules)")
                                s["last_batch_id"] = batch_id
                        except Exception as e:
                            logger.error(f"  → Failed to start batch: {e}")

                    # Update times
                    s["last_run_at"] = now.isoformat()
                    st = s.get("schedule_time", {})
                    s["next_run_at"] = _calc_next_run(st)
                    modified = True
                    logger.info(f"  → Next run: {s['next_run_at']}")

            if modified:
                _save_schedules(schedules)

        except Exception as e:
            logger.error(f"Schedule poller error: {e}")

        await asyncio.sleep(30)
