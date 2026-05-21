"""
Emotion rhythm schemas
"""

from typing import Optional
from pydantic import BaseModel, Field


class EmotionSegment(BaseModel):
    """情绪节奏片段"""
    index: int
    text: str
    start_time: float = Field(0, description="起始时间（秒）")
    end_time: float = Field(0, description="结束时间（秒）")
    emotion: str = Field("neutral", description="情绪标签：激昂/平静/疑问/感叹/悲伤")
    confidence: float = Field(0.0, description="情绪置信度 0-1")
    duration: float = Field(0, description="片段时长（秒）")


class EmotionRhythmResult(BaseModel):
    """情绪节奏分析结果"""
    video_name: str = ""
    total_duration: float = 0
    segments: list[EmotionSegment] = Field(default_factory=list)
    rhythm_profile: str = Field("", description="完整节奏 JSON")
    created_at: str = ""


class RhythmUploadResponse(BaseModel):
    """上传分析响应"""
    success: bool = True
    message: str = ""
    result: Optional[EmotionRhythmResult] = None
    analysis_id: Optional[str] = Field(None, description="分析结果持久化ID，用于后续 /update 和 /get")
