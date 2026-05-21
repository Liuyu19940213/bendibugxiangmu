"""
模型管理器 API schemas
"""

from typing import Optional
from pydantic import BaseModel, Field


class ModelInfo(BaseModel):
    name: str = Field(..., description="模型显示名称")
    key: str = Field(..., description="模型标识 key")
    category: str = Field(..., description="分类: asr / tts / image / emotion")
    size_mb: int = Field(..., description="模型大小 (MB)")
    downloaded: bool = Field(False, description="是否已下载到本地")
    local_path: str = Field("", description="本地模型路径")
    status: str = Field("unknown", description="状态: ready / downloading / not_downloaded")
    required_by: list[str] = Field(default_factory=list, description="哪些功能需要此模型")


class EnvironmentInfo(BaseModel):
    cuda_available: bool = Field(False, description="CUDA 是否可用")
    cuda_version: str = Field("", description="CUDA 版本")
    gpu_name: str = Field("", description="GPU 名称")
    vram_total_mb: int = Field(0, description="显存总量 (MB)")
    vram_free_mb: int = Field(0, description="可用显存 (MB)")
    python_version: str = Field("", description="Python 版本")
    torch_version: str = Field("", description="PyTorch 版本")
    ffmpeg_available: bool = Field(False, description="ffmpeg 是否可用")


class ModelStatusResponse(BaseModel):
    models: list[ModelInfo]
    environment: EnvironmentInfo


class ModelDownloadRequest(BaseModel):
    model_key: str = Field(..., description="要下载的模型 key")


class ModelDownloadResponse(BaseModel):
    success: bool
    message: str
    model_key: str
