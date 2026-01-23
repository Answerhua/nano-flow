"""Generation request and response schemas"""

from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
from .common import StepItem
from .visual import VisualPreferences


class GenerateRequest(BaseModel):
    """图像生成请求"""
    title: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="流程图主标题"
    )
    steps: List[StepItem] = Field(
        ...,
        min_length=2,
        max_length=6,
        description="步骤列表"
    )
    visual_preferences: VisualPreferences = Field(
        default_factory=VisualPreferences,
        description="视觉偏好配置"
    )
    seed: Optional[int] = Field(
        None,
        ge=0,
        description="随机种子（用于重现结果）"
    )
    
    @field_validator('steps')
    @classmethod
    def validate_steps_count(cls, v):
        if not (2 <= len(v) <= 6):
            raise ValueError('步骤数量必须在 2-6 之间')
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "title": "如何制作美味拿铁",
                "steps": [
                    {
                        "title": "研磨咖啡豆",
                        "description": "选择新鲜的中深烘焙豆子"
                    },
                    {
                        "title": "萃取浓缩",
                        "description": "使用咖啡机萃取双份Espresso"
                    }
                ],
                "visual_preferences": {
                    "character": "bear",
                    "color_scheme": "pastel",
                    "custom_tags": ["kawaii", "flat"]
                },
                "seed": None
            }
        }


class GenerateResponse(BaseModel):
    """生成任务创建响应"""
    task_id: str = Field(..., description="任务ID")
    status: str = Field(..., description="任务状态")
    message: str = Field(..., description="状态消息")
    
    class Config:
        json_schema_extra = {
            "example": {
                "task_id": "uuid-xxx-xxx",
                "status": "processing",
                "message": "正在分析需求... 🧠"
            }
        }
