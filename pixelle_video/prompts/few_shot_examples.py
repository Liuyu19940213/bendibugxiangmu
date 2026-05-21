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
Dynamic Few-shot Examples Database

Provides a structured database of example narrations for guiding LLM output.
Examples are categorized by:
- Topic type (technology, emotion, history, science, etc.)
- Language (zh, en)
- Style (healing, serious, humorous, inspirational, etc.)
"""

from typing import List, Dict, Optional, Literal, TypedDict
from enum import Enum
import json
from pathlib import Path


class TopicType(str, Enum):
    """Topic classification types"""
    TECHNOLOGY = "technology"
    EMOTION = "emotion"
    HISTORY = "history"
    SCIENCE = "science"
    HEALTH = "health"
    PSYCHOLOGY = "psychology"
