"""Image Generator Service - Nano Banana Pro API Integration"""

import httpx
import asyncio
from typing import Dict, Any, Optional
from loguru import logger

from ..config import settings


class ImageGenerator:
    """
    Nano Banana Pro 图像生成服务
    封装图像生成 API 调用逻辑
    """
    
    def __init__(self):
        self.api_key = settings.NANO_BANANA_API_KEY
        self.api_base = settings.NANO_BANANA_API_BASE
        self.model = settings.NANO_BANANA_MODEL
        self.default_width = settings.DEFAULT_IMAGE_WIDTH
        self.default_height = settings.DEFAULT_IMAGE_HEIGHT
        self.default_steps = settings.DEFAULT_STEPS
        self.default_cfg_scale = settings.DEFAULT_CFG_SCALE
    
    async def generate_image(
        self,
        prompt: str,
        negative_prompt: str = "",
        width: Optional[int] = None,
        height: Optional[int] = None,
        steps: Optional[int] = None,
        cfg_scale: Optional[float] = None,
        seed: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        生成图像
        
        Args:
            prompt: 正面提示词
            negative_prompt: 负面提示词
            width: 图片宽度
            height: 图片高度
            steps: 采样步数
            cfg_scale: CFG scale
            seed: 随机种子
            
        Returns:
            包含 image_url, seed 等信息的字典
        """
        # 使用默认值
        width = width or self.default_width
        height = height or self.default_height
        steps = steps or self.default_steps
        cfg_scale = cfg_scale or self.default_cfg_scale
        
        # 如果没有提供 seed，生成随机 seed
        if seed is None:
            import random
            seed = random.randint(0, 2**32 - 1)
        
        logger.info(f"Generating image with seed={seed}, size={width}x{height}")
        
        try:
            # 调用 Nano Banana Pro API
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    f"{self.api_base}/images/generations",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "negative_prompt": negative_prompt,
                        "width": width,
                        "height": height,
                        "steps": steps,
                        "guidance_scale": cfg_scale,
                        "seed": seed,
                        "num_images": 1
                    }
                )
                
                response.raise_for_status()
                result = response.json()
                
                # 解析响应
                image_url = self._extract_image_url(result)
                
                logger.info(f"Image generated successfully: {image_url[:50]}...")
                
                return {
                    "image_url": image_url,
                    "seed": seed,
                    "width": width,
                    "height": height,
                    "steps": steps,
                    "cfg_scale": cfg_scale,
                    "model": self.model
                }
                
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error during image generation: {e.response.status_code} - {e.response.text}")
            raise Exception(f"图像生成失败: HTTP {e.response.status_code}")
        except httpx.TimeoutException:
            logger.error("Image generation timeout")
            raise Exception("图像生成超时，请重试")
        except Exception as e:
            logger.error(f"Image generation failed: {e}")
            raise Exception(f"图像生成失败: {str(e)}")
    
    def _extract_image_url(self, response: Dict[str, Any]) -> str:
        """
        从 API 响应中提取图片 URL
        适配不同的 API 响应格式
        """
        # 尝试多种可能的响应格式
        if "data" in response and isinstance(response["data"], list):
            if len(response["data"]) > 0:
                item = response["data"][0]
                if "url" in item:
                    return item["url"]
                elif "b64_json" in item:
                    # 如果返回的是 base64，需要转换
                    return self._convert_base64_to_url(item["b64_json"])
        
        if "image_url" in response:
            return response["image_url"]
        
        if "url" in response:
            return response["url"]
        
        logger.error(f"Unexpected response format: {response}")
        raise ValueError("无法从响应中提取图片 URL")
    
    def _convert_base64_to_url(self, b64_data: str) -> str:
        """
        将 base64 图片数据转换为 data URL
        
        Note: 在生产环境中，应该上传到 OSS/CDN 并返回永久 URL
        """
        return f"data:image/png;base64,{b64_data}"
    
    async def create_thumbnail(
        self,
        image_url: str,
        max_width: int = 400,
        max_height: int = 300
    ) -> str:
        """
        创建缩略图
        
        Args:
            image_url: 原图 URL
            max_width: 最大宽度
            max_height: 最大高度
            
        Returns:
            缩略图 URL
            
        Note: 这是一个简化版本，实际应该下载图片、处理并上传到 CDN
        """
        # 简化实现：直接返回原图 URL
        # 在生产环境中，应该：
        # 1. 下载原图
        # 2. 使用 PIL 生成缩略图
        # 3. 上传到 OSS/CDN
        # 4. 返回缩略图 URL
        
        logger.info(f"Creating thumbnail for: {image_url[:50]}...")
        
        try:
            # 如果是 data URL，提取 base64 数据并处理
            if image_url.startswith("data:image"):
                return self._create_thumbnail_from_base64(image_url, max_width, max_height)
            
            # 对于远程 URL，这里简化为直接返回
            # TODO: 实现真正的缩略图生成
            return image_url
            
        except Exception as e:
            logger.error(f"Failed to create thumbnail: {e}")
            # 降级：返回原图
            return image_url
    
    def _create_thumbnail_from_base64(
        self,
        data_url: str,
        max_width: int,
        max_height: int
    ) -> str:
        """从 base64 data URL 创建缩略图"""
        try:
            from PIL import Image
            import io
            import base64
            
            # 提取 base64 数据
            base64_data = data_url.split(",")[1]
            image_data = base64.b64decode(base64_data)
            
            # 打开图片
            image = Image.open(io.BytesIO(image_data))
            
            # 生成缩略图
            image.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
            
            # 转换回 base64
            buffer = io.BytesIO()
            image.save(buffer, format="PNG")
            thumbnail_base64 = base64.b64encode(buffer.getvalue()).decode()
            
            return f"data:image/png;base64,{thumbnail_base64}"
            
        except ImportError:
            logger.warning("PIL not available, returning original image")
            return data_url
        except Exception as e:
            logger.error(f"Failed to create thumbnail from base64: {e}")
            return data_url
    
    async def check_model_status(self) -> Dict[str, Any]:
        """
        检查模型状态（健康检查）
        
        Returns:
            模型状态信息
        """
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"{self.api_base}/models",
                    headers={
                        "Authorization": f"Bearer {self.api_key}"
                    }
                )
                
                response.raise_for_status()
                return {
                    "status": "available",
                    "models": response.json()
                }
                
        except Exception as e:
            logger.error(f"Model status check failed: {e}")
            return {
                "status": "unavailable",
                "error": str(e)
            }
