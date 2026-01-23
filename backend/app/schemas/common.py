"""Common Pydantic models used across the application"""

from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class CharacterType(str, Enum):
    """可选的角色类型"""
    BEAR = "bear"
    CAT = "cat"
    RABBIT = "rabbit"
    DOG = "dog"
    PANDA = "panda"
    RANDOM = "random"


class ColorScheme(str, Enum):
    """可选的配色方案"""
    PASTEL = "pastel"  # 马卡龙色
    TECH_BLUE = "tech_blue"  # 科技蓝
    WARM_ORANGE = "warm_orange"  # 暖橙色
    MINT_GREEN = "mint_green"  # 薄荷绿
    PINK_PURPLE = "pink_purple"  # 粉紫色
    RANDOM = "random"


class StepItem(BaseModel):
    """流程步骤项"""
    title: str = Field(..., min_length=1, max_length=50, description="步骤标题")
    description: str = Field("", max_length=200, description="步骤描述")

    class Config:
        json_schema_extra = {
            "example": {
                "title": "研磨咖啡豆",
                "description": "选择新鲜的中深烘焙豆子"
            }
        }


class BaseResponse(BaseModel):
    """基础响应模型"""
    success: bool = Field(True, description="请求是否成功")
    message: str = Field("", description="响应消息")


class ErrorResponse(BaseModel):
    """错误响应模型"""
    success: bool = Field(False, description="请求是否成功")
    error: str = Field(..., description="错误信息")
    error_code: Optional[str] = Field(None, description="错误代码")
