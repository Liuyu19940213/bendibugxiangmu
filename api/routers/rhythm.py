"""
Emotion rhythm API endpoints

Features:
- POST /analyze: Analyze text and return emotion rhythm segments (saved to disk)
- POST /update:  Manually update a segment's emotion label (persisted)
- GET /{analysis_id}: Retrieve saved analysis result
"""

import hashlib
import json
from pathlib import Path
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from loguru import logger

from api.services.rhythm import analyze_emotion_rhythm
from api.schemas.rhythm import EmotionRhythmResult, RhythmUploadResponse, EmotionSegment


class RhythmAnalyzeRequest(BaseModel):
    """文本情绪分析请求"""
    text: str = Field(..., description="待分析文案")
    name: str = Field("", description="书名/视频名")


class RhythmUpdateRequest(BaseModel):
    """手动微调情绪请求"""
    analysis_id: str = Field(..., description="分析结果ID（从 /analyze 返回）")
    segment_index: int
    emotion: str
    text: str = ""


router = APIRouter(prefix="/rhythm", tags=["Emotion Rhythm"])


def _rhythm_dir() -> Path:
    from api.config import api_config
    d = Path(api_config.data_dir) / "rhythm"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _analysis_path(analysis_id: str) -> Path:
    return _rhythm_dir() / f"{analysis_id}.json"


def _text_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def _save_analysis(analysis_id: str, result: EmotionRhythmResult):
    sp = _analysis_path(analysis_id)
    with open(sp, "w", encoding="utf-8") as f:
        json.dump(result.model_dump(), f, ensure_ascii=False, indent=2)


def _load_analysis(analysis_id: str) -> dict:
    sp = _analysis_path(analysis_id)
    if not sp.exists():
        raise HTTPException(status_code=404, detail=f"Analysis not found: {analysis_id}")
    with open(sp, "r", encoding="utf-8") as f:
        return json.load(f)


@router.post("/analyze", response_model=RhythmUploadResponse)
async def analyze_rhythm(req: RhythmAnalyzeRequest):
    """分析文案情绪节奏（结果自动持久化）"""
    if not req.text.strip():
        raise HTTPException(status_code=400, detail="文本不能为空")

    try:
        result = analyze_emotion_rhythm(text=req.text, name=req.name)
        analysis_id = _text_hash(req.text)
        _save_analysis(analysis_id, result)
        logger.info(f"Analyzed & saved rhythm '{req.name}' ({analysis_id}): {len(result.segments)} segments")
        return RhythmUploadResponse(
            success=True,
            message="分析完成",
            result=result,
            analysis_id=analysis_id,
        )
    except Exception as e:
        logger.error(f"Rhythm analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/update")
async def update_segment(req: RhythmUpdateRequest):
    """
    手动微调某段的情绪标签（持久化到文件）

    刷新页面后修改不丢失。
    """
    try:
        data = _load_analysis(req.analysis_id)
        segments = data.get("segments", [])

        if req.segment_index < 0 or req.segment_index >= len(segments):
            raise HTTPException(
                status_code=400,
                detail=f"segment_index {req.segment_index} out of range (0-{len(segments) - 1})",
            )

        old_emotion = segments[req.segment_index]["emotion"]
        segments[req.segment_index]["emotion"] = req.emotion
        if req.text:
            segments[req.segment_index]["text"] = req.text

        # Rebuild result and save
        result = EmotionRhythmResult(**data)
        _save_analysis(req.analysis_id, result)

        logger.info(
            f"Updated segment {req.segment_index}: {old_emotion} → {req.emotion}"
            f" (analysis_id={req.analysis_id})"
        )

        return {
            "success": True,
            "message": f"已将第 {req.segment_index} 段情绪从 {old_emotion} 改为 {req.emotion}",
            "analysis_id": req.analysis_id,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Update segment failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{analysis_id}", response_model=RhythmUploadResponse)
async def get_analysis(analysis_id: str):
    """获取已保存的情绪分析结果"""
    try:
        data = _load_analysis(analysis_id)
        result = EmotionRhythmResult(**data)
        return RhythmUploadResponse(success=True, message="", result=result)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
