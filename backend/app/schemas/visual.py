"""Visual preferences related schemas"""

from pydantic import BaseModel, Field
from typing import List
from .common import CharacterType, ColorScheme


class VisualPreferences(BaseModel):
    """视觉偏好配置"""
    character: CharacterType = Field(
        default=CharacterType.RANDOM,
        description="角色类型"
    )
    color_scheme: ColorScheme = Field(
        default=ColorScheme.PASTEL,
        description="配色方案"
    )
    custom_tags: List[str] = Field(
        default_factory=list,
        max_length=10,
        description="自定义标签"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "character": "bear",
                "color_scheme": "pastel",
                "custom_tags": ["kawaii", "flat"]
            }
        }
