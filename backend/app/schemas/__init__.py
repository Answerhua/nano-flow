"""Pydantic schemas for request/response validation"""

from .common import (
    CharacterType,
    ColorScheme,
    StepItem,
    BaseResponse,
    ErrorResponse,
)
from .visual import VisualPreferences
from .task import (
    TaskStatus,
    ImageMetadata,
    GenerationResult,
    ErrorDetail,
    TaskResponse,
    TaskCreate,
)
from .generate import (
    GenerateRequest, 
    GenerateResponse,
    GenerateStepsRequest,
    GenerateStepsResponse
)
from .generate_vs import (
    ScenarioItem,
    GenerateVSRequest
)

__all__ = [
    # Common
    "CharacterType",
    "ColorScheme",
    "StepItem",
    "BaseResponse",
    "ErrorResponse",
    # Visual
    "VisualPreferences",
    # Task
    "TaskStatus",
    "ImageMetadata",
    "GenerationResult",
    "ErrorDetail",
    "TaskResponse",
    "TaskCreate",
    # Generate
    "GenerateRequest",
    "GenerateResponse",
    "GenerateStepsRequest",
    "GenerateStepsResponse",
    # Generate VS
    "ScenarioItem",
    "GenerateVSRequest",
]
