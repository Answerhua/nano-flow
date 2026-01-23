"""Task status related schemas"""

from enum import Enum
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime


class TaskStatus(str, Enum):
    """任务状态枚举"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class ImageMetadata(BaseModel):
    """生成图片的元数据"""
    resolution: str = Field(..., description="图片分辨率")
    seed: int = Field(..., description="随机种子")
    model_version: str = Field(..., description="模型版本")
    cfg_scale: float = Field(7.5, description="CFG scale")
    sampling_steps: int = Field(20, description="采样步数")
    
    class Config:
        json_schema_extra = {
            "example": {
                "resolution": "1344x768",
                "seed": 42,
                "model_version": "nano-banana-pro-v1",
                "cfg_scale": 7.5,
                "sampling_steps": 20
            }
        }


class GenerationResult(BaseModel):
    """生成结果"""
    image_url: str = Field(..., description="图片URL")
    thumbnail_url: str = Field(..., description="缩略图URL")
    enhanced_prompt: str = Field(..., description="增强后的提示词")
    metadata: ImageMetadata = Field(..., description="元数据")
    
    class Config:
        json_schema_extra = {
            "example": {
                "image_url": "https://cdn.example.com/images/xxx.png",
                "thumbnail_url": "https://cdn.example.com/images/xxx_thumb.png",
                "enhanced_prompt": "A cute white bear...",
                "metadata": {
                    "resolution": "1344x768",
                    "seed": 42,
                    "model_version": "nano-banana-pro-v1",
                    "cfg_scale": 7.5,
                    "sampling_steps": 20
                }
            }
        }


class ErrorDetail(BaseModel):
    """错误详情"""
    code: str = Field(..., description="错误代码")
    message: str = Field(..., description="错误消息")


class TaskResponse(BaseModel):
    """任务状态响应"""
    task_id: str = Field(..., description="任务ID")
    status: TaskStatus = Field(..., description="任务状态")
    progress: Optional[int] = Field(None, ge=0, le=100, description="进度百分比")
    message: str = Field("", description="状态消息")
    result: Optional[GenerationResult] = Field(None, description="生成结果")
    error: Optional[ErrorDetail] = Field(None, description="错误信息")
    estimated_time: Optional[int] = Field(None, description="预计剩余秒数")
    
    class Config:
        json_schema_extra = {
            "example": {
                "task_id": "uuid-xxx-xxx",
                "status": "processing",
                "progress": 45,
                "message": "正在给线条上色... 🎨",
                "estimated_time": 30
            }
        }


class TaskCreate(BaseModel):
    """创建任务记录（内部使用）"""
    title: str
    input_data: Dict[str, Any]
    user_id: Optional[str] = None
