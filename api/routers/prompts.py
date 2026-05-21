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
Prompt management endpoints

GET    /api/prompts/rewrite  – view current assembled prompts
PUT    /api/prompts/rewrite  – save custom assembled prompts
DELETE /api/prompts/rewrite – reset to defaults
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from loguru import logger

from pixelle_video.prompts.manager import (
    get_all_prompts,
    save_prompts,
    reset_prompt_config,
)

router = APIRouter(prefix="/prompts", tags=["Prompts"])


# ── Schemas ──

class RewritePromptResponse(BaseModel):
    """GET response: assembled prompts for both modes."""
    assembled_flexible: str = Field("", description="完整 flexible 模式 Prompt")
    assembled_rigid: str = Field("", description="完整 rigid 模式 Prompt")
    is_customized: bool = Field(False, description="用户是否已自定义")


class RewritePromptSaveRequest(BaseModel):
    """PUT request body."""
    assembled_flexible: str = Field("", description="flexible 模式完整 Prompt")
    assembled_rigid: str = Field("", description="rigid 模式完整 Prompt")


class RewritePromptSaveResponse(BaseModel):
    """PUT response."""
    success: bool = True
    message: str = "Saved"


class RewritePromptResetResponse(BaseModel):
    """DELETE response."""
    success: bool = True
    message: str = "Reset to defaults"


# ── Routes ──

@router.get("/rewrite", response_model=RewritePromptResponse)
async def get_rewrite_prompt():
    """Get current rewrite prompts (assembled full text for both modes)."""
    try:
        data = get_all_prompts()
        return RewritePromptResponse(
            assembled_flexible=data["assembled_flexible"],
            assembled_rigid=data["assembled_rigid"],
            is_customized=data["is_customized"],
        )
    except Exception as e:
        logger.error(f"Get rewrite prompt error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


REQUIRED_PLACEHOLDERS = ["{originality}", "{target_chars}"]


@router.put("/rewrite", response_model=RewritePromptSaveResponse)
async def update_rewrite_prompt(request: RewritePromptSaveRequest):
    """Save custom rewrite prompts for both modes."""
    # 校验必需的占位符
    missing_flexible = [p for p in REQUIRED_PLACEHOLDERS if p not in request.assembled_flexible]
    missing_rigid = [p for p in REQUIRED_PLACEHOLDERS if p not in request.assembled_rigid]
    errors = []
    if missing_flexible:
        errors.append(f"flexible 缺少占位符: {', '.join(missing_flexible)}")
    if missing_rigid:
        errors.append(f"rigid 缺少占位符: {', '.join(missing_rigid)}")
    if errors:
        raise HTTPException(status_code=400, detail="; ".join(errors))

    try:
        save_prompts(
            assembled_flexible=request.assembled_flexible,
            assembled_rigid=request.assembled_rigid,
        )
        return RewritePromptSaveResponse()
    except Exception as e:
        logger.error(f"Update rewrite prompt error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/rewrite", response_model=RewritePromptResetResponse)
async def reset_rewrite_prompt():
    """Reset rewrite prompts to hardcoded defaults."""
    try:
        reset_prompt_config()
        return RewritePromptResetResponse()
    except Exception as e:
        logger.error(f"Reset rewrite prompt error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
