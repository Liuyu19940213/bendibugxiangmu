"""
MiMo TTS Service — 小米 MiMo-V2.5-TTS 直连 API

通过 OpenAI 兼容的 Chat Completions 格式调用 MiMo 语音合成。
支持基础 TTS 和声音克隆。
"""

import base64
import uuid
from pathlib import Path
from typing import Optional

import httpx
from loguru import logger


class MimoTTSService:
    """MiMo TTS service using OpenAI-compatible Chat Completions API."""

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.mimo-v2.com/v1",
        voice: str = "mimo_default",
        voice_src_url: Optional[str] = None,
    ):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.voice = voice
        self.voice_src_url = voice_src_url

    async def synthesize(
        self,
        text: str,
        voice: Optional[str] = None,
        voice_src_url: Optional[str] = None,
        output_path: Optional[str] = None,
        format: str = "wav",
    ) -> str:
        """
        Synthesize speech from text.

        Args:
            text: Text to synthesize
            voice: Voice ID override (default: self.voice)
            voice_src_url: Reference audio URL for voice cloning (optional)
            output_path: Output file path (auto-generated if None)
            format: Audio format (wav / mp3 / pcm16)

        Returns:
            Audio file path
        """
        final_voice = voice or self.voice
        final_voice_src = voice_src_url or self.voice_src_url

        # Choose model based on whether voice cloning is requested
        if final_voice_src:
            model = "mimo-v2.5-tts-voiceclone"
            logger.info(f"🎙️  MiMo TTS (voice clone): voice={final_voice}, src={final_voice_src[:50]}...")
        else:
            model = "mimo-v2.5-tts"
            logger.info(f"🎙️  MiMo TTS: voice={final_voice}")

        # Build request
        messages = [
            {"role": "assistant", "content": text},
        ]
        audio_config = {"format": format, "voice": final_voice}

        request_body = {
            "model": model,
            "messages": messages,
            "audio": audio_config,
        }

        if final_voice_src:
            request_body["voice_src_url"] = final_voice_src

        timeout = httpx.Timeout(connect=10.0, read=120.0, write=30.0, pool=10.0)
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    json=request_body,
                    headers=headers,
                )
                response.raise_for_status()
                data = response.json()

            # Extract Base64 audio
            audio_data = data["choices"][0]["message"]["audio"]["data"]
            audio_bytes = base64.b64decode(audio_data)

            # Generate output path if not provided
            if not output_path:
                unique_id = uuid.uuid4().hex
                ext = format if format != "pcm16" else "wav"
                output_path = f"output/{unique_id}.{ext}"
                Path("output").mkdir(parents=True, exist_ok=True)

            # Write file
            with open(output_path, "wb") as f:
                f.write(audio_bytes)

            logger.info(f"✅ MiMo TTS generated: {output_path} ({len(audio_bytes)} bytes)")
            return output_path

        except httpx.HTTPStatusError as e:
            logger.error(f"MiMo TTS HTTP error: {e.response.status_code} — {e.response.text[:300]}")
            raise
        except Exception as e:
            logger.error(f"MiMo TTS error: {e}")
            raise
