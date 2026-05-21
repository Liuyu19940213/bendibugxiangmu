"""
Prompt Configuration Manager

Stores user-customized rewrite prompts as assembled full-text in prompts_config.json.
Falls back to Python hardcoded defaults when no custom config exists.
"""

import json
from pathlib import Path
from typing import Optional
from loguru import logger

# Default location: project root, same level as config.yaml
_DEFAULT_PATH = Path(__file__).resolve().parent.parent.parent / "prompts_config.json"

_DEFAULTS: Optional[dict] = None


def _get_defaults() -> dict:
    """Lazy-load default assembled prompts from rewrite.py."""
    global _DEFAULTS
    if _DEFAULTS is None:
        from pixelle_video.prompts import rewrite as _rw
        _DEFAULTS = {
            "assembled_rigid": _rw.REWRITE_SYSTEM_PROMPT_RIGID,
            "assembled_flexible": _rw.REWRITE_SYSTEM_PROMPT_FLEXIBLE,
        }
    return _DEFAULTS


def _config_path() -> Path:
    return _DEFAULT_PATH


def load_assembled_prompt(mode: str) -> str:
    """Load the assembled prompt for the given mode.

    Args:
        mode: "flexible" or "rigid"

    Returns:
        The full system prompt text (with {originality}/{target_chars} placeholders).
    """
    key = f"assembled_{mode}"
    path = _config_path()
    if path.exists():
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            rewrite = data.get("rewrite", {})
            if key in rewrite and rewrite[key].strip():
                logger.debug(f"Loaded custom prompt for '{mode}' from {path}")
                return rewrite[key]
        except Exception as e:
            logger.warning(f"Failed to load {path}, using defaults: {e}")
    return _get_defaults()[key]


def get_all_prompts() -> dict:
    """Get both assembled prompts and customized flag.

    Returns:
        dict with keys: assembled_flexible, assembled_rigid, is_customized
    """
    defaults = _get_defaults()
    result = {
        "assembled_flexible": defaults["assembled_flexible"],
        "assembled_rigid": defaults["assembled_rigid"],
        "is_customized": False,
    }
    path = _config_path()
    if path.exists():
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            rewrite = data.get("rewrite", {})
            if rewrite.get("assembled_flexible", "").strip():
                result["assembled_flexible"] = rewrite["assembled_flexible"]
                result["is_customized"] = True
            if rewrite.get("assembled_rigid", "").strip():
                result["assembled_rigid"] = rewrite["assembled_rigid"]
                result["is_customized"] = True
        except Exception as e:
            logger.warning(f"Failed to load {path}: {e}")
    return result


def save_prompts(assembled_flexible: str, assembled_rigid: str) -> None:
    """Save both assembled prompts to JSON file.

    Args:
        assembled_flexible: Full flexible-mode prompt with {originality}/{target_chars}
        assembled_rigid: Full rigid-mode prompt with {originality}/{target_chars}
    """
    path = _config_path()

    existing: dict = {}
    if path.exists():
        try:
            with open(path, "r", encoding="utf-8") as f:
                existing = json.load(f)
        except Exception:
            existing = {}

    existing["rewrite"] = {
        "assembled_flexible": assembled_flexible,
        "assembled_rigid": assembled_rigid,
    }

    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(existing, f, ensure_ascii=False, indent=2)
    logger.info(f"Saved custom prompts to {path}")


def reset_prompt_config() -> None:
    """Delete custom config, reverting to Python defaults."""
    path = _config_path()
    if path.exists():
        path.unlink()
        logger.info(f"Deleted {path}, prompts reset to defaults")


def is_customized() -> bool:
    """Check whether user has customized prompts (has actual content, not just an empty file)."""
    path = _config_path()
    if not path.exists():
        return False
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        rewrite = data.get("rewrite", {})
        return bool(
            rewrite.get("assembled_flexible", "").strip()
            or rewrite.get("assembled_rigid", "").strip()
        )
    except Exception:
        return False
