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
Batch task API schemas
"""

from typing import Optional, Dict, Any, Literal
from pydantic import BaseModel, Field


ModuleStatusType = Literal[
    "idle",
    "pending",
    "running",
    "completed",
    "failed",
    "skipped",
    "cancelled"
]


class ModuleStatus:
    """模块运行状态常量"""
    IDLE = "idle"
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"
    CANCELLED = "cancelled"


class RewriteParams(BaseModel):
    """文案洗稿参数"""
    reference_count: int = Field(3, ge=0, le=10, description="对标素材数量")
    style: str = Field("沉稳大气", description="风格描述")
    target_words_min: int = Field(3000, ge=100, le=10000, description="目标中文字数最小值")
    target_words_max: int = Field(4500, ge=100, le=10000, description="目标中文字数最大值")


class GlobalConfig(BaseModel):
    """全局默认配置"""
    voice_id: str = Field("", description="配音音色标识")
    voice_type: Literal["clone", "tts"] = Field("tts", description="配音方式")
    bgm_path: str = Field("", description="BGM 文件路径")
    bgm_style: Literal["激昂", "宁静"] = Field("宁静", description="BGM 风格")
    duration_min: int = Field(480, ge=60, le=1800, description="视频目标时长最小值（秒）")
    duration_max: int = Field(780, ge=60, le=1800, description="视频目标时长最大值（秒）")
    visual_style: str = Field("风景意境", description="画面风格")
    rewrite_params: RewriteParams = Field(default_factory=RewriteParams)


class BatchModuleRequest(BaseModel):
    """单个批量创作模块请求"""
    id: str = Field(..., description="模块唯一标识")
    book_name: str = Field(..., description="书名")
    raw_text: str = Field("", description="预置文案")
    enabled: bool = Field(True, description="是否启用")
    config_override: Optional[Dict[str, Any]] = Field(None, description="单模块配置覆盖")
    sort_order: int = Field(0, description="模块创建顺序")


class BatchRunRequest(BaseModel):
    """批量运行请求"""
    modules: list[BatchModuleRequest] = Field(..., description="模块列表")
    global_config: GlobalConfig = Field(..., description="全局默认配置")

    class Config:
        json_schema_extra = {
            "example": {
                "modules": [
                    {
                        "id": "module-001",
                        "book_name": "书名1",
                        "raw_text": "文案内容...",
                        "enabled": True,
                        "sort_order": 0
                    }
                ],
                "global_config": {
                    "voice_id": "clone_001",
                    "voice_type": "clone",
                    "bgm_path": "",
                    "bgm_style": "宁静",
                    "duration_min": 480,
                    "duration_max": 780,
                    "visual_style": "风景意境",
                    "rewrite_params": {
                        "reference_count": 3,
                        "style": "沉稳大气",
                        "target_words_min": 3000,
                        "target_words_max": 4500
                    }
                }
            }
        }


class BatchRunResponse(BaseModel):
    """批量运行响应"""
    success: bool = True
    message: str = "批量任务已启动"
    batch_id: str = Field(..., description="批量任务ID，用于后续查询")


class ModuleStatusDetail(BaseModel):
    """单个模块状态详情"""
    id: str
    book_name: str
    status: ModuleStatusType
    enabled: bool
    error_message: Optional[str] = None
    sort_order: int = 0
    result: Optional[Dict[str, Any]] = None


class BatchProgress(BaseModel):
    """批量运行进度"""
    total: int = Field(0, description="总模块数")
    completed: int = Field(0, description="已完成数")
    failed: int = Field(0, description="失败数")
    skipped: int = Field(0, description="跳过数")
    current_book: Optional[str] = Field(None, description="当前处理书名")
    percent: float = Field(0.0, description="进度百分比 0-100")
    current_module_id: Optional[str] = Field(None, description="当前处理模块ID")


class BatchStatusResponse(BaseModel):
    """批量任务状态响应"""
    batch_id: str
    status: ModuleStatusType
    progress: BatchProgress
    modules: list[ModuleStatusDetail]
    created_at: str
    started_at: Optional[str] = None
    completed_at: Optional[str] = None


class BatchCancelResponse(BaseModel):
    """取消批量任务响应"""
    success: bool = True
    message: str = "批量任务已取消"
    batch_id: str


class ModuleStatusResponse(BaseModel):
    """单个模块状态响应"""
    batch_id: str
    module: ModuleStatusDetail


class UnfinishedBatchInfo(BaseModel):
    """未完成的批量任务信息"""
    batch_id: str
    created_at: str
    progress: BatchProgress
    module_count: int


class CheckUnfinishedResponse(BaseModel):
    """检查未完成任务响应"""
    has_unfinished: bool = Field(False, description="是否有未完成任务")
    unfinished_batches: list[UnfinishedBatchInfo] = Field(default_factory=list)


class ResumeBatchRequest(BaseModel):
    """恢复批量任务请求"""
    batch_id: str = Field(..., description="要恢复的批量任务ID")


class ResumeBatchResponse(BaseModel):
    """恢复批量任务响应"""
    success: bool = True
    message: str = "批量任务已恢复"
    batch_id: str


class ModuleTraceMeta(BaseModel):
    """模块文案溯源元数据"""
    source_hash: str = Field("", description="原文 SHA256")
    originality: Optional[float] = Field(None, description="原创度 0-1")
    reference_count: int = Field(0, description="对标素材数量")
    char_count: int = Field(0, description="洗稿后中文字数")
    rewrite_date: Optional[str] = Field(None, description="洗稿时间 ISO8601")
    book_name: str = Field("", description="书名")


class BatchHistoryItem(BaseModel):
    """运行历史列表项"""
    batch_id: str
    created_at: str
    completed_at: Optional[str] = None
    status: str
    total_modules: int = 0
    completed_modules: int = 0
    failed_modules: int = 0
    global_config: Optional[Dict[str, Any]] = None


class BatchHistoryDetail(BaseModel):
    """运行历史详情（含溯源）"""
    batch_id: str
    created_at: str
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    status: str
    global_config: Optional[Dict[str, Any]] = None
    modules: list[ModuleTraceMeta] = Field(default_factory=list)
