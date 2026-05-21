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
LLM (Large Language Model) endpoints
"""

from fastapi import APIRouter, HTTPException
from loguru import logger
from openai import AsyncOpenAI
import httpx

from api.dependencies import PixelleVideoDep
from api.schemas.llm import LLMChatRequest, LLMChatResponse, LLMTestRequest, LLMTestResponse

router = APIRouter(prefix="/llm", tags=["Basic Services"])


@router.post("/chat", response_model=LLMChatResponse)
async def llm_chat(
    request: LLMChatRequest,
    pixelle_video: PixelleVideoDep
):
    """
    LLM chat endpoint
    
    Generate text response using configured LLM.
    
    - **prompt**: User prompt/question
    - **temperature**: Creativity level (0.0-2.0, lower = more deterministic)
    - **max_tokens**: Maximum response length
    
    Returns generated text response.
    """
    try:
        logger.info(f"LLM chat request: {request.prompt[:50]}...")
        
        # Call LLM service
        response = await pixelle_video.llm(
            prompt=request.prompt,
            temperature=request.temperature,
            max_tokens=request.max_tokens
        )
        
        return LLMChatResponse(
            content=response,
            tokens_used=None  # Can add token counting if needed
        )
        
    except Exception as e:
        logger.error(f"LLM chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/test", response_model=LLMTestResponse)
async def llm_test(request: LLMTestRequest):
    """
    Test LLM API connectivity

    Creates a temporary OpenAI client with the given credentials
    and sends a minimal chat request.
    """
    try:
        logger.info(f"LLM test request: provider={request.provider}, model={request.model}")

        client = AsyncOpenAI(
            base_url=request.api_base,
            api_key=request.api_key,
            timeout=httpx.Timeout(15.0, connect=10.0),
        )

        resp = await client.chat.completions.create(
            model=request.model,
            messages=[{"role": "user", "content": "Reply with just OK"}],
            max_tokens=5,
            temperature=0,
        )

        content = resp.choices[0].message.content or ""
        return LLMTestResponse(
            ok=True,
            detail=f"连接成功，模型响应：{content[:80]}"
        )

    except Exception as e:
        logger.error(f"LLM test error: {e}")
        return LLMTestResponse(
            ok=False,
            detail=str(e)
        )

