"""
Scheduled task schemas
"""

from typing import Optional, Literal
from pydantic import BaseModel, Field


class ScheduleTime(BaseModel):
    """定时时间配置"""
    hour: int = Field(8, ge=0, le=23)
    minute: int = Field(0, ge=0, le=59)
    weekdays: list[int] = Field(default_factory=lambda: [0, 1, 2, 3, 4, 5, 6])


class ScheduleConfig(BaseModel):
    """定时任务配置"""
    id: Optional[str] = None
    name: str = Field("", description="任务名称")
    enabled: bool = Field(True)
    schedule_time: ScheduleTime = Field(default_factory=ScheduleTime)
    template_id: Optional[str] = Field(None, description="使用的模块模板ID")
    last_run_at: Optional[str] = None
    next_run_at: Optional[str] = None
    created_at: Optional[str] = None


class ScheduleListResponse(BaseModel):
    """定时任务列表"""
    schedules: list[ScheduleConfig] = Field(default_factory=list)


class ScheduleCreateRequest(BaseModel):
    """创建定时任务请求"""
    name: str
    schedule_time: ScheduleTime
    template_id: Optional[str] = None
    template_data: Optional[dict] = Field(None, description="模板完整数据（global_config + modules）")


class ScheduleUpdateRequest(BaseModel):
    """更新定时任务请求"""
    name: Optional[str] = None
    enabled: Optional[bool] = None
    schedule_time: Optional[ScheduleTime] = None
    template_id: Optional[str] = None
