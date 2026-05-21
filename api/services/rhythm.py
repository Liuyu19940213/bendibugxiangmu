"""
Emotion rhythm analysis service

Analyzes text to infer emotion rhythm from punctuation, keywords, and structure.
Replaces Whisper-based transcription with pure text analysis for offline use.
"""

import re
import json
from datetime import datetime
from api.schemas.rhythm import EmotionSegment, EmotionRhythmResult


EMOTION_KEYWORDS: dict[str, list[str]] = {
    "激昂": ["震撼", "惊人", "突破", "巅峰", "奇迹", "爆发", "逆袭", "绝地", "碾压", "轰动", "必须", "一定", "绝对"],
    "悲伤": ["遗憾", "可惜", "难过", "心痛", "眼泪", "悲伤", "无奈", "叹息", "失去", "离别", "痛苦", "哭泣"],
    "疑问": ["为什么", "难道", "怎么", "如何", "真的吗", "不可思议", "你会", "你想过", "是否"],
    "感叹": ["天哪", "啊", "原来", "竟然", "居然", "太", "多么", "简直", "如此", "实在"],
    "平静": ["慢慢", "渐渐", "日常", "平凡", "习惯", "安静", "淡淡", "岁月", "时光", "生活"],
}


def _split_sentences(text: str) -> list[str]:
    """Split text into sentences by Chinese punctuation"""
    parts = re.split(r"([。！？；\n])", text)
    sentences: list[str] = []
    buf = ""
    for p in parts:
        if p in ("。", "！", "？", "；", "\n"):
            buf += p
            if buf.strip():
                sentences.append(buf.strip())
            buf = ""
        else:
            buf += p
    if buf.strip():
        sentences.append(buf.strip())
    return sentences


def _infer_emotion(sentence: str) -> tuple[str, float]:
    """Infer emotion from punctuation and keywords"""
    scores: dict[str, int] = {}

    for emotion, keywords in EMOTION_KEYWORDS.items():
        score = 0
        for kw in keywords:
            score += sentence.count(kw)
        scores[emotion] = score

    if sentence.endswith("！"):
        scores["激昂"] = scores.get("激昂", 0) + 2
        scores["感叹"] = scores.get("感叹", 0) + 1
    elif sentence.endswith("？"):
        scores["疑问"] = scores.get("疑问", 0) + 2
    elif sentence.endswith("……") or sentence.endswith("…"):
        scores["悲伤"] = scores.get("悲伤", 0) + 1

    max_emotion = max(scores, key=lambda k: scores[k])
    max_score = scores[max_emotion]

    if max_score == 0:
        return ("平静", 0.5)

    total = sum(scores.values()) or 1
    confidence = min(0.95, max_score / max(total / len(scores), 1) * 0.8 + 0.2)
    return (max_emotion, round(confidence, 2))


def analyze_emotion_rhythm(
    text: str,
    name: str = "",
    char_per_second: float = 4.5,
) -> EmotionRhythmResult:
    """
    Analyze text and produce emotion rhythm profile

    Args:
        text: Input Chinese text
        name: Video/book name
        char_per_second: Average characters per second for duration estimation

    Returns:
        EmotionRhythmResult with segments and profile
    """
    sentences = _split_sentences(text)
    segments: list[EmotionSegment] = []
    elapsed = 0.0

    for idx, sentence in enumerate(sentences):
        emotion, confidence = _infer_emotion(sentence)
        duration = max(1.0, len(sentence) / char_per_second)

        segment = EmotionSegment(
            index=idx,
            text=sentence,
            start_time=round(elapsed, 2),
            end_time=round(elapsed + duration, 2),
            emotion=emotion,
            confidence=confidence,
            duration=round(duration, 2),
        )
        segments.append(segment)
        elapsed += duration

    profile = json.dumps(
        {
            "name": name,
            "segment_count": len(segments),
            "emotions": [s.emotion for s in segments],
            "confidence": [s.confidence for s in segments],
        },
        ensure_ascii=False,
    )

    return EmotionRhythmResult(
        video_name=name,
        total_duration=round(elapsed, 2),
        segments=segments,
        rhythm_profile=profile,
        created_at=datetime.now().isoformat(),
    )
