"""Application configuration management"""

from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List

CURRENT_FILE_DIR = Path(__file__).resolve().parent
ENV_FILE_PATH = CURRENT_FILE_DIR / ".env"


class Settings(BaseSettings):
    """Application settings from environment variables"""
    
    # API Keys
    QWEN_API_KEY: str
    GRSAI_API_KEY: str  # GRSAI API 密钥（用于 Nano Banana Pro）
    
    # API Base URLs
    QWEN_API_BASE: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    GRSAI_API_BASE: str = "https://grsai.dakka.com.cn"  # GRSAI API 基础地址
    
    # Application Settings
    APP_ENV: str = "development"
    APP_DEBUG: bool = True
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000
    
    # CORS Settings
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:3000"]
    
    # Generation Settings
    DEFAULT_IMAGE_WIDTH: int = 1344
    DEFAULT_IMAGE_HEIGHT: int = 768
    DEFAULT_STEPS: int = 20
    DEFAULT_CFG_SCALE: float = 7.5
    MAX_STEPS_COUNT: int = 6
    MIN_STEPS_COUNT: int = 2
    
    # LLM Settings
    LLM_MODEL: str = "qwen-turbo"
    LLM_TEMPERATURE: float = 0.7
    LLM_MAX_TOKENS: int = 1000
    
    # GRSAI Nano Banana Settings
    GRSAI_MODEL: str = "nano-banana-pro"  # 可选: nano-banana-fast, nano-banana-pro, nano-banana-pro-vip 等
    GRSAI_IMAGE_SIZE: str = "1K"  # 可选: 1K, 2K, 4K
    GRSAI_ASPECT_RATIO: str = "auto"  # 可选: auto, 16:9, 9:16, 1:1 等
    GRSAI_POLL_INTERVAL: int = 2  # 轮询间隔（秒）
    GRSAI_MAX_POLL_ATTEMPTS: int = 2.5 * 60  # 最大轮询次数（5秒*60=300秒）
    
    model_config = SettingsConfigDict(
        env_file=ENV_FILE_PATH,
        env_file_encoding="utf-8",
        case_sensitive=True
    )


# Global settings instance
settings = Settings()
