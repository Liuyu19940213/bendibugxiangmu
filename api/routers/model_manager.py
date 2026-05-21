"""
模型管理器 API — 环境检测 + 模型状态 + 一键下载
"""

import os
import shutil
from pathlib import Path

from fastapi import APIRouter, HTTPException
from loguru import logger

from api.schemas.model_manager import (
    ModelInfo,
    EnvironmentInfo,
    ModelStatusResponse,
    ModelDownloadRequest,
    ModelDownloadResponse,
)

router = APIRouter(prefix="/models", tags=["Model Manager"])

# ── 模型定义 ──

_MODEL_DEFINITIONS: list[dict] = [
    {
        "key": "whisper-tiny",
        "name": "Whisper Tiny",
        "category": "asr",
        "size_mb": 150,
        "required_by": ["视频转文案（低精度）"],
        "hf_repo": "openai/whisper-tiny",
        "file": "tiny.pt",
    },
    {
        "key": "whisper-base",
        "name": "Whisper Base",
        "category": "asr",
        "size_mb": 280,
        "required_by": ["视频转文案（快速）"],
        "hf_repo": "openai/whisper-base",
        "file": "base.pt",
    },
    {
        "key": "whisper-small",
        "name": "Whisper Small",
        "category": "asr",
        "size_mb": 920,
        "required_by": ["视频转文案（均衡）"],
        "hf_repo": "openai/whisper-small",
        "file": "small.pt",
    },
    {
        "key": "whisper-medium",
        "name": "Whisper Medium",
        "category": "asr",
        "size_mb": 1500,
        "required_by": ["视频转文案（推荐）"],
        "hf_repo": "openai/whisper-medium",
        "file": "medium.pt",
    },
    {
        "key": "cosyvoice2",
        "name": "CosyVoice 2",
        "category": "tts",
        "size_mb": 3000,
        "required_by": ["本地 TTS 配音（主力）", "声音克隆 + 情感标签"],
        "hf_repo": "FunAudioLLM/CosyVoice2-0.5B",
    },
    {
        "key": "indextts2",
        "name": "IndexTTS-2",
        "category": "tts",
        "size_mb": 4000,
        "required_by": ["本地 TTS 配音（备用）", "声音克隆"],
        "hf_repo": "IndexTeam/Index-TTS",
    },
    {
        "key": "speechbrain-emotion",
        "name": "SpeechBrain 情绪分析",
        "category": "emotion",
        "size_mb": 300,
        "required_by": ["音频情绪分析", "情绪驱动配音"],
        "hf_repo": "speechbrain/emotion-recognition-wav2vec2-IEMOCAP",
    },
    {
        "key": "sdxl-base",
        "name": "SDXL 1.0 Base",
        "category": "image",
        "size_mb": 7000,
        "required_by": ["AI 生图（推荐）", "高画质配图"],
        "hf_repo": "stabilityai/stable-diffusion-xl-base-1.0",
    },
]


def _get_models_dir() -> Path:
    """获取模型存储根目录（应用目录/models 优先）"""
    env_dir = os.environ.get("PIXELLE_MODELS_DIR", "")
    if env_dir:
        return Path(env_dir)
    app_dir = os.environ.get("PIXELLE_APP_DIR", "")
    if app_dir:
        return Path(app_dir) / "models"
    try:
        from api.config import api_config
        return Path(api_config.data_dir) / "models"
    except ImportError:
        return Path("data") / "models"


def _get_whisper_dir() -> Path:
    """Whisper 模型目录"""
    base = os.environ.get("WHISPER_MODEL_DIR", "")
    if base:
        return Path(base)
    return _get_models_dir() / "whisper"


def _check_whisper_model(key: str) -> tuple[bool, str]:
    """检查 Whisper 模型是否已下载"""
    fname = f"{key.replace('whisper-', '')}.pt"
    p = _get_whisper_dir() / fname
    if p.exists():
        return True, str(p)
    return False, ""


def _check_cosyvoice() -> tuple[bool, str]:
    """检查 CosyVoice2 模型"""
    import importlib.util
    has_cv = importlib.util.find_spec("cosyvoice") is not None
    model_dir = _get_models_dir() / "cosyvoice2"
    if model_dir.exists() and any(model_dir.iterdir()):
        return True, str(model_dir)
    return has_cv, ""


def _check_indextts() -> tuple[bool, str]:
    """检查 IndexTTS-2 模型（通过 ComfyUI 加载）"""
    model_dir = _get_models_dir() / "indextts2"
    if model_dir.exists() and any(model_dir.iterdir()):
        return True, str(model_dir)
    return False, ""


def _check_sdxl() -> tuple[bool, str]:
    """检查 SDXL 模型"""
    model_dir = _get_models_dir() / "sdxl"
    if model_dir.exists() and any(model_dir.iterdir()):
        return True, str(model_dir)
    return False, ""


def _check_speechbrain() -> tuple[bool, str]:
    """检查 SpeechBrain 情绪模型"""
    import importlib.util
    has_sb = importlib.util.find_spec("speechbrain") is not None
    model_dir = _get_models_dir() / "speechbrain"
    if model_dir.exists() and any(model_dir.iterdir()):
        return True, str(model_dir)
    return has_sb, ""


_MODEL_CHECKERS = {
    "whisper-tiny": _check_whisper_model,
    "whisper-base": _check_whisper_model,
    "whisper-small": _check_whisper_model,
    "whisper-medium": _check_whisper_model,
    "cosyvoice2": _check_cosyvoice,
    "indextts2": _check_indextts,
    "sdxl-base": _check_sdxl,
    "speechbrain-emotion": _check_speechbrain,
}


def _collect_environment() -> EnvironmentInfo:
    """收集环境信息"""
    info = EnvironmentInfo()

    # CUDA
    try:
        import torch
        info.cuda_available = torch.cuda.is_available()
        if info.cuda_available:
            info.cuda_version = torch.version.cuda or ""
            props = torch.cuda.get_device_properties(0)
            info.gpu_name = props.name
            info.vram_total_mb = props.total_mem // (1024 * 1024)
            info.vram_free_mb = (props.total_mem - torch.cuda.memory_allocated(0)) // (1024 * 1024)
        info.torch_version = torch.__version__
    except ImportError:
        logger.debug("torch 未安装，无法检测 CUDA 环境")

    # Python
    import sys
    info.python_version = sys.version.split()[0]

    # ffmpeg
    info.ffmpeg_available = shutil.which("ffmpeg") is not None

    return info


def _do_download_hf(repo: str, target_dir: Path) -> bool:
    """通过 huggingface_hub 下载模型"""
    os.environ.setdefault("HF_ENDPOINT", "https://hf-mirror.com")
    try:
        from huggingface_hub import snapshot_download
        snapshot_download(
            repo_id=repo,
            local_dir=str(target_dir),
            local_dir_use_symlinks=False,
            resume_download=True,
        )
        return True
    except ImportError:
        logger.error("huggingface_hub 未安装，请运行: uv add huggingface-hub")
        return False
    except Exception as e:
        logger.error(f"下载 {repo} 失败: {e}")
        return False


def _do_download_whisper(key: str) -> bool:
    """下载 Whisper 模型"""
    import whisper
    os.environ.setdefault("HF_ENDPOINT", "https://hf-mirror.com")
    size = key.replace("whisper-", "")
    target_dir = str(_get_whisper_dir())
    target_dir_path = Path(target_dir)
    target_dir_path.mkdir(parents=True, exist_ok=True)

    expected = target_dir_path / f"{size}.pt"
    if expected.exists():
        return True

    try:
        whisper.load_model(size, download_root=target_dir)
        return expected.exists()
    except Exception as e:
        logger.error(f"下载 Whisper {size} 失败: {e}")
        return False


@router.get("/status", response_model=ModelStatusResponse)
def get_model_status():
    """获取所有模型状态和环境信息"""
    models: list[ModelInfo] = []
    for defn in _MODEL_DEFINITIONS:
        checker = _MODEL_CHECKERS.get(defn["key"])
        downloaded = False
        local_path = ""
        if checker:
            downloaded, local_path = checker(defn["key"])

        models.append(ModelInfo(
            name=defn["name"],
            key=defn["key"],
            category=defn["category"],
            size_mb=defn["size_mb"],
            downloaded=downloaded,
            local_path=local_path,
            status="ready" if downloaded else "not_downloaded",
            required_by=defn["required_by"],
        ))

    return ModelStatusResponse(
        models=models,
        environment=_collect_environment(),
    )


@router.post("/download", response_model=ModelDownloadResponse)
def download_model(req: ModelDownloadRequest):
    """下载指定模型（如已存在则跳过）"""
    key = req.model_key
    defn = next((d for d in _MODEL_DEFINITIONS if d["key"] == key), None)
    if defn is None:
        raise HTTPException(status_code=400, detail=f"未知模型: {key}")

    # 检查是否已下载
    checker = _MODEL_CHECKERS.get(key)
    if checker:
        downloaded, local_path = checker(key)
        if downloaded:
            return ModelDownloadResponse(
                success=False,
                message=f"{defn['name']} 已存在 ({local_path})，无需重复下载",
                model_key=key,
            )

    target_dir = _get_models_dir() / key
    target_dir.mkdir(parents=True, exist_ok=True)

    success = False
    # Whisper 模型走专用下载
    if key.startswith("whisper-"):
        success = _do_download_whisper(key)
    else:
        # 通用 HuggingFace 下载
        if "hf_repo" in defn:
            success = _do_download_hf(defn["hf_repo"], target_dir)

    if success:
        return ModelDownloadResponse(
            success=True,
            message=f"{defn['name']} 下载完成 → {target_dir}",
            model_key=key,
        )
    else:
        return ModelDownloadResponse(
            success=False,
            message=f"{defn['name']} 下载失败，请检查网络或手动放置模型到 {target_dir}",
            model_key=key,
        )


@router.post("/download-all")
def download_all_models():
    """一键下载所有缺失模型"""
    results = []
    for defn in _MODEL_DEFINITIONS:
        checker = _MODEL_CHECKERS.get(defn["key"])
        if checker:
            downloaded, _ = checker(defn["key"])
            if downloaded:
                results.append({"key": defn["key"], "status": "skipped", "message": "已存在"})
                continue

        success = False
        if defn["key"].startswith("whisper-"):
            success = _do_download_whisper(defn["key"])
        elif "hf_repo" in defn:
            target_dir = _get_models_dir() / defn["key"]
            target_dir.mkdir(parents=True, exist_ok=True)
            success = _do_download_hf(defn["hf_repo"], target_dir)

        results.append({
            "key": defn["key"],
            "status": "success" if success else "failed",
            "message": "下载完成" if success else "下载失败",
        })

    return {"results": results}
