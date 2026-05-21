"""
Batch module executor callback

Bridges batch_manager's execution loop with the actual video generation pipeline.
Registered in api/app.py lifespan startup via batch_manager.set_execution_callback().
"""

import os
from pathlib import Path
from loguru import logger

from pixelle_video import pixelle_video


async def execute_module(
    module,          # BatchModuleState
    global_config,   # GlobalConfig (from api.schemas.batch)
    batch_id: str,
    module_index: int,
    total_modules: int,
) -> dict:
    """
    Execute a single batch module: take pre-written text → generate video.

    Merges global_config with module.config_override for per-module customization.
    Since batch mode uses pre-written scripts (不洗稿), this uses mode="fixed".

    Returns:
        dict with keys: video_path, duration, file_size, output_dir
    """
    # Merge config: global → override
    cfg = global_config.model_dump() if hasattr(global_config, "model_dump") else dict(global_config)
    override = module.config_override or {}
    cfg.update(override)

    text = (module.raw_text or "").strip()
    title = (module.book_name or "untitled").strip()
    bgm_path = cfg.get("bgm_path", "")
    bgm_volume = 0.3

    logger.info(
        f"[Batch {batch_id}] Module {module_index + 1}/{total_modules}: "
        f"\"{title}\" ({len(text)} chars, bgm={bgm_path or 'none'})"
    )

    # Estimate scene count from text length
    char_count = len(text)
    n_scenes = max(3, min(15, char_count // 450))

    # Resolve frame template
    frame_template = cfg.get("frame_template") or "1080x1920/image_default.html"

    # Build video params
    video_params = {
        "text": text,
        "mode": "fixed",
        "title": title,
        "n_scenes": n_scenes,
        "frame_template": frame_template,
        "bgm_path": bgm_path or None,
        "bgm_volume": bgm_volume,
    }

    # Optional local image paths (from module override)
    image_paths = cfg.get("image_paths")
    if image_paths:
        valid_paths = [p for p in image_paths if os.path.exists(p)]
        if valid_paths:
            video_params["image_paths"] = valid_paths

    # TTS config
    if cfg.get("tts_speed") is not None:
        video_params["tts_speed"] = cfg["tts_speed"]

    logger.debug(f"[Batch {batch_id}] video_params: { {k: v for k, v in video_params.items() if k != 'text'} }")

    result = await pixelle_video.generate_video(**video_params)

    video_path = str(result.video_path) if hasattr(result, "video_path") else ""
    duration = result.duration if hasattr(result, "duration") else 0
    file_size = os.path.getsize(video_path) if video_path and os.path.exists(video_path) else 0

    output = {
        "video_path": video_path,
        "duration": duration,
        "file_size": file_size,
        "output_dir": str(Path(video_path).parent) if video_path else "",
    }

    logger.info(
        f"[Batch {batch_id}] Module complete: \"{title}\" → "
        f"{duration:.1f}s, {file_size / 1024 / 1024:.1f}MB"
    )

    return output
