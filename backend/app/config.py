"""Application configuration management"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    """Application settings from environment variables"""
    
    # API Keys
    QWEN_API_KEY: str
    NANO_BANANA_API_KEY: str
    
    # API Base URLs
    QWEN_API_BASE: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    NANO_BANANA_API_BASE: str = "https://api.nanobanana.ai/v1"
    
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
    
    # Nano Banana Settings
    NANO_BANANA_MODEL: str = "nano-banana-pro-v1"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True
    )


# Global settings instance
settings = Settings()
