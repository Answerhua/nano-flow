"""Generation VS (comparison) request and response schemas"""

from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
from .visual import VisualPreferences


class ScenarioItem(BaseModel):
    """场景项（左侧/右侧）"""
    title: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="场景标题"
    )
    description: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="场景描述（角色状态、环境等）"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "title": "不好的学习方法",
                "description": "被动、枯燥、混乱、疲惫"
            }
        }


class GenerateVSRequest(BaseModel):
    """VS 对比图生成请求"""
    title: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="对比主题标题（显示在图片最上方）"
    )
    left_scenario: ScenarioItem = Field(
        ...,
        description="左侧场景（通常为反面教材/不好的例子）"
    )
    right_scenario: ScenarioItem = Field(
        ...,
        description="右侧场景（通常为正面教材/好的例子）"
    )
    actions: List[str] = Field(
        ...,
        min_length=2,
        max_length=6,
        description="建议的行动/正确做法列表（显示在图片底部）"
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
    
    @field_validator('actions')
    @classmethod
    def validate_actions_count(cls, v):
        if not (2 <= len(v) <= 6):
            raise ValueError('建议行动数量必须在 2-6 之间')
        return v
    
    @field_validator('actions')
    @classmethod
    def validate_action_length(cls, v):
        for action in v:
            if len(action) > 30:
                raise ValueError('每个建议行动不能超过 30 个字符')
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "title": "不好的学习方法 vs 好的学习方法",
                "left_scenario": {
                    "title": "不好的学习方法",
                    "description": "被动、枯燥、混乱、疲惫"
                },
                "right_scenario": {
                    "title": "好的学习方法",
                    "description": "主动、清晰、轻松"
                },
                "actions": [
                    "设定目标",
                    "深度理解",
                    "主动输出",
                    "定期复盘"
                ],
                "visual_preferences": {
                    "character": "bear",
                    "color_scheme": "pastel",
                    "custom_tags": ["kawaii", "flat"]
                },
                "seed": None
            }
        }
