# Copyright (C) 2025 AIDC-AI
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#     http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Content generation API schemas
"""

from typing import List, Optional
from pydantic import BaseModel, Field


# ============================================================================
# Narration Generation
# ============================================================================

class NarrationGenerateRequest(BaseModel):
    """Narration generation request"""
    text: str = Field(..., description="Source text to generate narrations from")
    n_scenes: int = Field(5, ge=1, le=20, description="Number of scenes")
    min_words: int = Field(5, ge=1, le=5000, description="Minimum words per narration")
    max_words: int = Field(20, ge=1, le=5000, description="Maximum words per narration")
    
    class Config:
        json_schema_extra = {
            "example": {
                "text": "Atomic Habits is about making small changes that lead to remarkable results.",
                "n_scenes": 5,
                "min_words": 5,
                "max_words": 20
            }
        }


class NarrationGenerateResponse(BaseModel):
    """Narration generation response"""
    success: bool = True
    message: str = "Success"
    narrations: List[str] = Field(..., description="Generated narrations")


# ============================================================================
# Image Prompt Generation
# ============================================================================

class ImagePromptGenerateRequest(BaseModel):
    """Image prompt generation request"""
    narrations: List[str] = Field(..., description="List of narrations")
    min_words: int = Field(30, ge=10, le=100, description="Minimum words per prompt")
    max_words: int = Field(60, ge=10, le=200, description="Maximum words per prompt")
    
    class Config:
        json_schema_extra = {
            "example": {
                "narrations": [
                    "Small habits compound over time",
                    "Focus on systems, not goals"
                ],
                "min_words": 30,
                "max_words": 60
            }
        }


class ImagePromptGenerateResponse(BaseModel):
    """Image prompt generation response"""
    success: bool = True
    message: str = "Success"
    image_prompts: List[str] = Field(..., description="Generated image prompts")


# ============================================================================
# Title Generation
# ============================================================================

class TitleGenerateRequest(BaseModel):
    """Title generation request"""
    text: str = Field(..., description="Source text")
    style: Optional[str] = Field(None, description="Title style (e.g., 'engaging', 'formal')")
    
    class Config:
        json_schema_extra = {
            "example": {
                "text": "Atomic Habits is about making small changes that lead to remarkable results.",
                "style": "engaging"
            }
        }


class TitleGenerateResponse(BaseModel):
    """Title generation response"""
    success: bool = True
    message: str = "Success"
    title: str = Field(..., description="Generated title")


# ============================================================================
# Dynamic Few-shot Rewrite
# ============================================================================

class RewriteRequest(BaseModel):
    """Dynamic few-shot rewrite request"""
    text: str = Field(..., description="原文")
    book_name: str = Field("", description="书名（用于素材匹配）")
    reference_count: int = Field(3, ge=0, le=10, description="对标素材数量")
    originality: int = Field(30, ge=10, le=80, description="原创度百分比")
    target_chars: str = Field("3000-4500", description="目标字数范围")
    rewrite_mode: str = Field("flexible", description="洗稿模式：rigid=锁骨架 | flexible=首尾锁·中段自由")


class RewriteMeta(BaseModel):
    """溯源元数据，嵌入导出文件头部，方便用户追溯评价"""
    book_name: str = ""
    date: str = ""
    originality: int = 30
    reference_count: int = 0
    source_hash: str = ""
    target_chars: str = ""
    rewrite_mode: str = "flexible"


class RewriteResponse(BaseModel):
    """Rewrite response - plain text + traceability metadata"""
    success: bool = True
    message: str = "Success"
    content: str = Field("", description="洗稿结果（纯文本）")
    reference_count: int = Field(0, description="实际使用的对标素材数量")
    meta: RewriteMeta = Field(default_factory=RewriteMeta, description="溯源元数据")

