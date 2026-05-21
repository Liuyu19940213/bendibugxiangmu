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
Content generation endpoints

Endpoints for generating narrations, image prompts, and titles.
"""

from fastapi import APIRouter, HTTPException
from loguru import logger
from pydantic import BaseModel, Field

from api.dependencies import PixelleVideoDep
from api.schemas.content import (
    NarrationGenerateRequest,
    NarrationGenerateResponse,
    ImagePromptGenerateRequest,
    ImagePromptGenerateResponse,
    TitleGenerateRequest,
    TitleGenerateResponse,
    RewriteRequest,
    RewriteResponse,
    RewriteMeta,
)
from pixelle_video.utils.content_generators import (
    generate_narrations_from_content,
    generate_image_prompts,
    generate_title,
)

router = APIRouter(prefix="/content", tags=["Content Generation"])


@router.post("/narration", response_model=NarrationGenerateResponse)
async def generate_narration(
    request: NarrationGenerateRequest,
    pixelle_video: PixelleVideoDep
):
    """
    Generate narrations from text
    
    Uses LLM to break down text into multiple narration segments.
    
    - **text**: Source text
    - **n_scenes**: Number of narrations to generate
    - **min_words**: Minimum words per narration
    - **max_words**: Maximum words per narration
    
    Returns list of narration strings.
    """
    try:
        logger.info(f"Generating {request.n_scenes} narrations from text")
        
        # Call narration generator utility function (content refinement mode)
        narrations = await generate_narrations_from_content(
            llm_service=pixelle_video.llm,
            content=request.text,
            n_scenes=request.n_scenes,
            min_words=request.min_words,
            max_words=request.max_words
        )
        
        return NarrationGenerateResponse(
            narrations=narrations
        )
        
    except Exception as e:
        logger.error(f"Narration generation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/image-prompt", response_model=ImagePromptGenerateResponse)
async def generate_image_prompt(
    request: ImagePromptGenerateRequest,
    pixelle_video: PixelleVideoDep
):
    """
    Generate image prompts from narrations
    
    Uses LLM to create detailed image generation prompts.
    
    - **narrations**: List of narration texts
    - **min_words**: Minimum words per prompt
    - **max_words**: Maximum words per prompt
    
    Returns list of image prompts.
    """
    try:
        logger.info(f"Generating image prompts for {len(request.narrations)} narrations")
        
        # Call image prompt generator utility function
        image_prompts = await generate_image_prompts(
            llm_service=pixelle_video.llm,
            narrations=request.narrations,
            min_words=request.min_words,
            max_words=request.max_words
        )
        
        return ImagePromptGenerateResponse(
            image_prompts=image_prompts
        )
        
    except Exception as e:
        logger.error(f"Image prompt generation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/title", response_model=TitleGenerateResponse)
async def generate_title_endpoint(
    request: TitleGenerateRequest,
    pixelle_video: PixelleVideoDep
):
    """
    Generate video title from text
    
    Uses LLM to create an engaging title.
    
    - **text**: Source text
    - **style**: Optional title style hint
    
    Returns generated title.
    """
    try:
        logger.info("Generating title from text")
        
        # Call title generator utility function
        title = await generate_title(
            llm_service=pixelle_video.llm,
            content=request.text,
            strategy="llm"
        )
        
        return TitleGenerateResponse(
            title=title
        )
        
    except Exception as e:
        logger.error(f"Title generation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/rewrite", response_model=RewriteResponse)
async def rewrite_content(
    request: RewriteRequest,
    pixelle_video: PixelleVideoDep,
):
    """
    Dynamic few-shot rewrite endpoint

    Matches reference articles by book name, deduplicates,
    injects as few-shot examples, and generates rewritten content.
    """
    try:
        from pixelle_video.prompts.rewrite import build_system_prompt, build_rewrite_user_message
        from pixelle_video.services.material_library import MaterialLibrary

        # Match reference materials
        library = MaterialLibrary()
        references: list[str] = []
        if request.book_name.strip() and request.reference_count > 0:
            references = library.select_references(request.book_name, request.reference_count)

        logger.info(
            f"Rewrite: book={request.book_name}, refs={len(references)}, "
            f"originality={request.originality}%"
        )

        # Build messages
        system_prompt = build_system_prompt(
            mode=request.rewrite_mode,
            originality=request.originality,
            target_chars=request.target_chars,
        )
        user_message = build_rewrite_user_message(request.text, references)

        # Call LLM directly (system + user dual messages)
        # with provider-aware options and 3-retry backoff
        import asyncio
        from openai import AsyncOpenAI, APIStatusError
        from pixelle_video.config import config_manager

        cfg = config_manager.config.llm
        client = AsyncOpenAI(
            api_key=cfg.api_key,
            base_url=cfg.base_url,
            timeout=120.0,
        )

        # Build create_kwargs, only add reasoning_effort for DeepSeek
        create_kwargs: dict = {
            "model": cfg.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            "temperature": 0.7,
            "max_tokens": 5000,
        }
        if cfg.provider == "deepseek":
            create_kwargs["extra_body"] = {"reasoning_effort": "high"}

        content = ""
        last_error: Exception | None = None
        for attempt in range(3):
            try:
                response = await client.chat.completions.create(**create_kwargs)
                content = response.choices[0].message.content or ""
                break
            except APIStatusError as exc:
                last_error = exc
                if exc.status_code == 401:
                    raise
                if exc.status_code == 429 or exc.status_code >= 500:
                    if attempt < 2:
                        await asyncio.sleep(2 ** attempt)
                        continue
                raise
            except Exception as exc:
                last_error = exc
                if attempt < 2:
                    await asyncio.sleep(2 ** attempt)
                else:
                    raise

        if not content and last_error:
            raise last_error

        # Build traceability metadata (do NOT auto-save to library)
        import hashlib
        from datetime import datetime
        source_hash = hashlib.sha256(request.text.encode("utf-8")).hexdigest()[:12]

        meta = RewriteMeta(
            book_name=request.book_name,
            date=datetime.now().strftime("%Y-%m-%d %H:%M"),
            originality=request.originality,
            reference_count=len(references),
            source_hash=source_hash,
            target_chars=request.target_chars,
            rewrite_mode=request.rewrite_mode,
        )

        return RewriteResponse(
            content=content,
            reference_count=len(references),
            meta=meta,
        )

    except Exception as e:
        logger.error(f"Rewrite error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


class SaveToLibraryRequest(BaseModel):
    """Request to manually add a reviewed rewrite result to the material library"""
    book_name: str = Field(..., description="书名")
    content: str = Field(..., description="洗稿结果（纯文本）")


class SaveToLibraryResponse(BaseModel):
    success: bool = True
    message: str = "Success"
    saved: bool = Field(False, description="是否实际保存（去重可能跳过）")


@router.post("/rewrite/save-to-library", response_model=SaveToLibraryResponse)
async def save_to_library(request: SaveToLibraryRequest):
    """
    Manually save a reviewed rewrite result to the material library.

    Only call this after the user has reviewed and approved the content.
    Deduplication is applied: near-duplicates are silently skipped.
    """
    try:
        from pixelle_video.services.material_library import MaterialLibrary

        library = MaterialLibrary()
        saved = library.save(request.book_name, request.content)
        logger.info(
            f"Manual save to library: book={request.book_name}, saved={saved}"
        )
        return SaveToLibraryResponse(
            saved=saved,
            message="已保存" if saved else "已存在重复，跳过",
        )
    except Exception as e:
        logger.error(f"Save to library error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

