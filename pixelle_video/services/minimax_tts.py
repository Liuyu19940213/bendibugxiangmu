"""
MiniMax TTS Service — 海螺 Speech 2.8 HD 直连 API

通过 MiniMax T2A v2 API 调用海螺语音合成。
支持声音克隆（需预先通过 MiniMax 生成 voice_id）。
"""

import uuid
from pathlib import Path
from typing import Optional

import httpx
from loguru import logger


class MinimaxTTSService:
    """MiniMax Speech 2.8 HD TTS service using T2A v2 API."""

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.minimax.chat/v1",
        voice_id: str = "default_voice",
        speed: float = 1.0,
        vol: float = 1.0,
        pitch: float = 0.0,
    ):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.voice_id = voice_id
        self.speed = speed
        self.vol = vol
        self.pitch = pitch

    async def synthesize(
        self,
        text: str,
        voice_id: Optional[str] = None,
        speed: Optional[float] = None,
        vol: Optional[float] = None,
        pitch: Optional[float] = None,
        output_path: Optional[str] = None,
        format: str = "mp3",
    ) -> str:
        """
        Synthesize speech from text using MiniMax Speech 2.8 HD.

        Args:
            text: Text to synthesize
            voice_id: MiniMax voice_id (supports cloned voices)
            speed: Speech speed (0.5 - 2.0, default 1.0)
            vol: Volume (0.1 - 10.0, default 1.0)
            pitch: Pitch adjustment (-12 to 12, default 0)
            output_path: Output file path (auto-generated if None)
            format: Audio format (mp3 / wav / pcm)

        Returns:
            Audio file path
        """
        final_voice_id = voice_id or self.voice_id
        final_speed = speed if speed is not None else self.speed
        final_vol = vol if vol is not None else self.vol
        final_pitch = pitch if pitch is not None else self.pitch

        logger.info(
            f"🎙️  MiniMax TTS: voice_id={final_voice_id}, speed={final_speed}, "
            f"vol={final_vol}, pitch={final_pitch}"
        )

        request_body = {
            "model": "speech-2.8-hd",
            "text": text,
            "stream": False,
            "voice_setting": {
                "voice_id": final_voice_id,
                "speed": final_speed,
                "vol": final_vol,
                "pitch": final_pitch,
            },
            "audio_setting": {
                "sample_rate": 32000,
                "channel": 1,
                "format": format,
            },
        }

        timeout = httpx.Timeout(connect=10.0, read=120.0, write=30.0, pool=10.0)
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.post(
                    f"{self.base_url}/t2a_v2",
                    json=request_body,
                    headers=headers,
                )
                response.raise_for_status()
                data = response.json()

            base_resp = data.get("base_resp", {})
            if base_resp.get("status_code") != 0:
                error_msg = base_resp.get("status_msg", "Unknown error")
                raise Exception(f"MiniMax API error: {error_msg} (code: {base_resp.get('status_code')})")

            audio_hex = data["data"]["audio"]
            audio_bytes = bytes.fromhex(audio_hex)

            if not output_path:
                unique_id = uuid.uuid4().hex
                ext = format if format != "pcm" else "wav"
                output_path = f"output/{unique_id}.{ext}"
                Path("output").mkdir(parents=True, exist_ok=True)

            with open(output_path, "wb") as f:
                f.write(audio_bytes)

            logger.info(f"✅ MiniMax TTS generated: {output_path} ({len(audio_bytes)} bytes)")
            return output_path

        except httpx.HTTPStatusError as e:
            logger.error(f"MiniMax TTS HTTP error: {e.response.status_code} — {e.response.text[:300]}")
            raise
        except Exception as e:
            logger.error(f"MiniMax TTS error: {e}")
            raise
