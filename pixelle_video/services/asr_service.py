"""
ASR Service — Whisper 语音转文字

将音频文件转录为纯文本，支持多档模型切换。
无需预置模型文件：首次使用时自动从 HuggingFace 下载。
"""

import os
from pathlib import Path
from typing import Optional, Literal, Callable

from loguru import logger

WhisperModelSize = Literal["tiny", "base", "small", "medium", "large-v3"]

_MODEL_META = {
    "tiny":      {"url": "https://huggingface.co/openai/whisper-tiny/resolve/main",         "size_mb": 72},
    "base":      {"url": "https://huggingface.co/openai/whisper-base/resolve/main",         "size_mb": 141},
    "small":     {"url": "https://huggingface.co/openai/whisper-small/resolve/main",        "size_mb": 465},
    "medium":    {"url": "https://huggingface.co/openai/whisper-medium/resolve/main",       "size_mb": 1467},
    "large-v3":  {"url": "https://huggingface.co/openai/whisper-large-v3/resolve/main",     "size_mb": 2910},
}

_model_cache: dict[str, object] = {}
_model_downloading: dict[str, bool] = {}


def _whisper_available() -> bool:
    try:
        import whisper
        return True
    except ImportError:
        return False


def _get_model_dir() -> Path:
    base = os.environ.get("WHISPER_MODEL_DIR", "")
    if base:
        return Path(base)
    app_dir = os.environ.get("PIXELLE_APP_DIR", "")
    if app_dir:
        return Path(app_dir) / "models" / "whisper"
    try:
        from pixelle_video.utils.os_util import get_data_path
        return Path(get_data_path("models", "whisper"))
    except ImportError:
        return Path("data") / "models" / "whisper"


def _check_model_downloaded(size: str) -> bool:
    """Check if whisper model is already cached locally."""
    expected = _get_model_dir() / f"{size}.pt"
    if expected.exists():
        return True
    return False


def get_model_status(size: str = "medium") -> dict:
    """Return download status of a model without loading it."""
    meta = _MODEL_META.get(size, _MODEL_META["medium"])
    downloaded = _check_model_downloaded(size)
    return {
        "model": size,
        "size_mb": meta["size_mb"],
        "downloaded": downloaded,
        "cache_dir": str(_get_model_dir()),
    }


def _load_model(size: WhisperModelSize, progress_callback: Optional[Callable[[str, float], None]] = None):
    """Load whisper model, downloading if needed. Calls progress_callback(state, percent)."""
    if not _whisper_available():
        raise RuntimeError(
            "openai-whisper 未安装。请运行: pip install openai-whisper"
        )

    import whisper

    if size in _model_cache:
        return _model_cache[size]

    meta = _MODEL_META.get(size, _MODEL_META["medium"])
    model_key = whisper._MODELS[size]  # e.g. "medium"

    downloaded = _check_model_downloaded(size)
    if not downloaded:
        logger.info(f"📥 首次使用，正在下载 Whisper 模型 {size}（约 {meta['size_mb']}MB）...")
        if progress_callback:
            progress_callback("downloading", 0.0)

    try:
        # whisper.load_model uses tqdm for progress — but it prints to stderr.
        # We suppress tqdm and use our own progress tracking.
        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            logger.info(f"🤖 加载 Whisper 模型: {size}")
            model = whisper.load_model(size, download_root=str(_get_model_dir()))
    except Exception as e:
        logger.error(f"❌ 加载 Whisper 模型失败: {e}")
        # Network error — give clear message
        if "Connection" in str(e) or "timeout" in str(e) or "resolve" in str(e):
            raise RuntimeError(
                f"下载 Whisper 模型 {size} 失败：网络不可达。\n"
                f"请检查网络连接，确保能访问 HuggingFace (huggingface.co)。\n"
                f"或手动下载模型放到 {_get_model_dir()} 目录。\n"
                f"原始错误: {e}"
            )
        raise

    if progress_callback:
        progress_callback("loaded", 1.0)

    _model_cache[size] = model
    logger.info(f"✅ Whisper 模型就绪: {size}")
    return model


async def transcribe_audio(
    audio_path: str,
    model_size: WhisperModelSize = "medium",
    language: Optional[str] = None,
    output_path: Optional[str] = None,
    progress_callback: Optional[Callable[[str, float], None]] = None,
) -> dict:
    """
    Transcribe audio to text using Whisper.

    Downloads model automatically on first use (cached permanently thereafter).

    Args:
        audio_path: Path to audio file (.wav, .mp3, etc.)
        model_size: Whisper model size (tiny/base/small/medium/large-v3)
        language: Language code (None = auto-detect, 'zh' for Chinese)
        output_path: Save transcript to file (optional)
        progress_callback: Optional callback(state: str, percent: float)

    Returns:
        dict with keys: text, segments, language
    """
    model = _load_model(model_size, progress_callback)

    transcribe_opts = {
        "verbose": False,
        "condition_on_previous_text": False,
        "fp16": False,  # fp16 on CUDA can fail with certain torch builds
    }
    if language:
        transcribe_opts["language"] = language

    logger.info(f"🎙️  转写中: {audio_path} (model={model_size})")
    if progress_callback:
        progress_callback("transcribing", 0.1)

    result = model.transcribe(audio_path, **transcribe_opts)

    if progress_callback:
        progress_callback("transcribing", 0.9)

    text = result.get("text", "").strip()
    segments = [
        {"start": round(s["start"], 2), "end": round(s["end"], 2), "text": s["text"].strip()}
        for s in result.get("segments", [])
    ]
    detected_language = result.get("language", "unknown")

    if output_path:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(text)
        logger.info(f"💾 转写文本已保存: {output_path}")

    if progress_callback:
        progress_callback("done", 1.0)

    logger.info(f"✅ 转写完成: {len(text)} 字符, {len(segments)} 段落, 语言={detected_language}")
    return {
        "text": text,
        "segments": segments,
        "language": detected_language,
    }


def unload_models():
    """Free GPU memory by unloading all cached models."""
    global _model_cache
    _model_cache.clear()
    logger.info("🗑️  已释放所有 Whisper 模型内存")


def preload_model(size: WhisperModelSize = "medium", progress_callback: Optional[Callable[[str, float], None]] = None):
    """
    Preload a model into memory (useful for warming up before batch processing).
    Since whisper.load_model is sync, wrap in a sync call — callers should use loop.run_in_executor.
    """
    return _load_model(size, progress_callback)
