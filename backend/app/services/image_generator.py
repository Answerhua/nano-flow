"""Image Generator Service - GRSAI Nano Banana Pro API Integration"""

import httpx
import asyncio
from typing import Dict, Any, Optional, Callable
from loguru import logger

from ..config import settings


class ImageGenerator:
    """
    GRSAI Nano Banana Pro 图像生成服务
    使用 GRSAI API 调用 Nano Banana Pro 模型
    """
    
    def __init__(self):
        self.api_key = settings.GRSAI_API_KEY
        self.api_base = settings.GRSAI_API_BASE
        self.model = settings.GRSAI_MODEL
        self.image_size = settings.GRSAI_IMAGE_SIZE
        self.aspect_ratio = settings.GRSAI_ASPECT_RATIO
        self.poll_interval = settings.GRSAI_POLL_INTERVAL
        self.max_poll_attempts = settings.GRSAI_MAX_POLL_ATTEMPTS
        
        # 分辨率映射（用于返回元数据）
        self.size_resolution_map = {
            "1K": {"16:9": "1920x1080", "9:16": "1080x1920", "1:1": "1024x1024", "auto": "1344x768"},
            "2K": {"16:9": "2560x1440", "9:16": "1440x2560", "1:1": "2048x2048", "auto": "2048x1152"},
            "4K": {"16:9": "3840x2160", "9:16": "2160x3840", "1:1": "4096x4096", "auto": "3840x2160"}
        }
    
    async def generate_image(
        self,
        prompt: str,
        negative_prompt: str = "",
        width: Optional[int] = None,
        height: Optional[int] = None,
        steps: Optional[int] = None,
        cfg_scale: Optional[float] = None,
        seed: Optional[int] = None,
        aspect_ratio: Optional[str] = None,
        image_size: Optional[str] = None,
        model: Optional[str] = None,
        reference_urls: Optional[list] = None,
        progress_callback: Optional[Callable[[int, str], None]] = None
    ) -> Dict[str, Any]:
        """
        生成图像
        
        Args:
            prompt: 正面提示词
            negative_prompt: 负面提示词（GRSAI 会自动处理，可以拼接到 prompt）
            width: 图片宽度（忽略，使用 aspect_ratio）
            height: 图片高度（忽略，使用 aspect_ratio）
            steps: 采样步数（忽略，GRSAI 自动处理）
            cfg_scale: CFG scale（忽略，GRSAI 自动处理）
            seed: 随机种子（GRSAI 不支持，保留用于元数据）
            aspect_ratio: 图片比例（16:9, 9:16, 1:1 等）
            image_size: 图片大小（1K, 2K, 4K）
            model: 模型名称
            reference_urls: 参考图 URL 列表
            progress_callback: 进度回调函数
            
        Returns:
            包含 image_url, seed 等信息的字典
        """
        # 使用传入的参数或默认值
        aspect_ratio = aspect_ratio or self.aspect_ratio
        image_size = image_size or self.image_size
        model = model or self.model
        
        # 如果提供了负面提示词，拼接到主提示词
        full_prompt = prompt
        if negative_prompt:
            full_prompt = f"{prompt}\n\nNegative prompt: {negative_prompt}"
        
        # 生成或使用提供的种子
        if seed is None:
            import random
            seed = random.randint(0, 2**32 - 1)
        
        logger.info(f"Generating image with GRSAI: model={model}, size={image_size}, ratio={aspect_ratio}")
        
        try:
            # 第一步：提交生成任务，获取任务 ID
            task_id = await self._submit_task(
                model=model,
                prompt=full_prompt,
                aspect_ratio=aspect_ratio,
                image_size=image_size,
                reference_urls=reference_urls
            )
            
            logger.info(f"Task submitted successfully, task_id: {task_id}")
            
            # 第二步：轮询获取结果
            result = await self._poll_result(
                task_id=task_id,
                progress_callback=progress_callback
            )
            
            # 提取图片 URL
            image_url = result["results"][0]["url"]
            
            # 获取实际分辨率
            resolution = self._get_resolution(image_size, aspect_ratio)
            
            logger.info(f"Image generated successfully: {image_url[:50]}...")
            
            return {
                "image_url": image_url,
                "seed": seed,
                "width": int(resolution.split("x")[0]),
                "height": int(resolution.split("x")[1]),
                "steps": 20,  # GRSAI 不返回步数，使用默认值
                "cfg_scale": 7.5,  # GRSAI 不返回 CFG，使用默认值
                "model": model,
                "task_id": task_id
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
    
    async def _submit_task(
        self,
        model: str,
        prompt: str,
        aspect_ratio: str,
        image_size: str,
        reference_urls: Optional[list] = None
    ) -> str:
        """
        提交生成任务，立即返回任务 ID
        
        Args:
            model: 模型名称
            prompt: 提示词
            aspect_ratio: 图片比例
            image_size: 图片大小
            reference_urls: 参考图 URL 列表
            
        Returns:
            任务 ID
        """
        url = f"{self.api_base}/v1/draw/nano-banana"
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model,
            "prompt": prompt,
            "aspectRatio": aspect_ratio,
            "imageSize": image_size,
            "webHook": "-1",  # 立即返回 ID，不使用回调
            "shutProgress": False  # 不关闭进度，用于轮询
        }
        
        # 添加参考图（如果提供）
        if reference_urls:
            payload["urls"] = reference_urls
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            result = response.json()
            
            # 检查响应
            if result.get("code") != 0:
                raise Exception(f"提交任务失败: {result.get('msg', 'Unknown error')}")
            
            task_id = result["data"]["id"]
            return task_id
    
    async def _poll_result(
        self,
        task_id: str,
        progress_callback: Optional[Callable] = None
    ) -> Dict[str, Any]:
        """
        轮询获取生成结果
        
        Args:
            task_id: 任务 ID
            progress_callback: 进度回调函数（异步） (progress: int, status: str)
            
        Returns:
            生成结果
        """
        url = f"{self.api_base}/v1/draw/result"
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "id": task_id
        }
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            for attempt in range(self.max_poll_attempts):
                try:
                    response = await client.post(url, headers=headers, json=payload)
                    response.raise_for_status()
                    result = response.json()
                    
                    # 检查响应码
                    if result.get("code") == -22:
                        raise Exception("任务不存在")
                    
                    if result.get("code") != 0:
                        raise Exception(f"查询失败: {result.get('msg', 'Unknown error')}")
                    
                    data = result["data"]
                    status = data.get("status", "")
                    progress = data.get("progress", 0)
                    
                    # 调用进度回调（支持异步）
                    if progress_callback:
                        if asyncio.iscoroutinefunction(progress_callback):
                            await progress_callback(progress, status)
                        else:
                            progress_callback(progress, status)
                    
                    logger.info(f"Task {task_id}: status={status}, progress={progress}%")
                    
                    # 检查任务状态
                    if status == "succeeded":
                        logger.info(f"Task {task_id} completed successfully")
                        return data
                    
                    elif status == "failed":
                        failure_reason = data.get("failure_reason", "")
                        error = data.get("error", "")
                        error_msg = self._format_error_message(failure_reason, error)
                        logger.error(f"Task {task_id} failed: {error_msg}")
                        raise Exception(f"生成失败: {error_msg}")
                    
                    # 任务进行中，等待后继续轮询
                    await asyncio.sleep(self.poll_interval)
                    
                except httpx.HTTPError as e:
                    logger.warning(f"Poll attempt {attempt + 1} failed: {e}")
                    if attempt < self.max_poll_attempts - 1:
                        await asyncio.sleep(self.poll_interval)
                    else:
                        raise
            
            # 超过最大轮询次数
            raise Exception(f"任务超时: 已轮询 {self.max_poll_attempts} 次仍未完成")
    
    def _format_error_message(self, failure_reason: str, error: str) -> str:
        """格式化错误消息"""
        error_map = {
            "output_moderation": "输出内容违规，请修改提示词",
            "input_moderation": "输入内容违规，请检查提示词",
            "error": f"系统错误: {error}"
        }
        
        return error_map.get(failure_reason, f"{failure_reason}: {error}")
    
    def _get_resolution(self, image_size: str, aspect_ratio: str) -> str:
        """
        根据图片大小和比例获取分辨率
        
        Args:
            image_size: 1K, 2K, 4K
            aspect_ratio: auto, 16:9, 9:16, 1:1 等
            
        Returns:
            分辨率字符串，如 "1920x1080"
        """
        return self.size_resolution_map.get(image_size, {}).get(aspect_ratio, "1344x768")
    
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
            
        Note: GRSAI 返回的图片 URL 有效期为 2 小时
              在生产环境中应该下载图片并上传到自己的 CDN
        """
        logger.info(f"Creating thumbnail for: {image_url[:50]}...")
        
        try:
            # 如果是普通 HTTP(S) URL，直接返回（简化实现）
            if image_url.startswith("http"):
                # TODO: 在生产环境中应该：
                # 1. 下载原图
                # 2. 使用 PIL 生成缩略图
                # 3. 上传到 OSS/CDN
                # 4. 返回缩略图 URL
                logger.warning("Thumbnail creation skipped, returning original URL")
                return image_url
            
            # 对于 data URL，尝试创建缩略图
            if image_url.startswith("data:image"):
                return self._create_thumbnail_from_base64(image_url, max_width, max_height)
            
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
        检查 GRSAI 服务状态（健康检查）
        
        Returns:
            服务状态信息
        """
        try:
            # 简单的健康检查：尝试访问 API 基础地址
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(
                    f"{self.api_base}",
                    headers={"Authorization": f"Bearer {self.api_key}"}
                )
                
                return {
                    "status": "available" if response.status_code < 500 else "degraded",
                    "api_base": self.api_base,
                    "model": self.model
                }
                
        except Exception as e:
            logger.error(f"Model status check failed: {e}")
            return {
                "status": "unavailable",
                "error": str(e)
            }
    
    def get_supported_models(self) -> list:
        """
        获取支持的模型列表
        
        Returns:
            模型名称列表
        """
        return [
            "nano-banana-fast",      # 快速版（推荐，性价比高）
            "nano-banana",           # 基础版
            "nano-banana-pro",       # 标准专业版
            "nano-banana-pro-vt",    # 专业版（旧通道）
            "nano-banana-pro-cl",    # 高级专业版
            "nano-banana-pro-vip",   # VIP 版（1K/2K）
            "nano-banana-pro-4k-vip" # VIP 4K 版
        ]
    
    def get_supported_sizes(self, model: str = None) -> list:
        """
        获取支持的图片大小
        
        Args:
            model: 模型名称（某些模型有限制）
            
        Returns:
            大小列表
        """
        model = model or self.model
        
        # VIP 1K/2K 版本只支持 1K 和 2K
        if model == "nano-banana-pro-vip":
            return ["1K", "2K"]
        
        # VIP 4K 版本只支持 4K
        if model == "nano-banana-pro-4k-vip":
            return ["4K"]
        
        # 其他模型支持全部
        return ["1K", "2K", "4K"]
    
    def get_supported_aspect_ratios(self) -> list:
        """
        获取支持的图片比例
        
        Returns:
            比例列表
        """
        return [
            "auto",
            "1:1",
            "16:9",
            "9:16",
            "4:3",
            "3:4",
            "3:2",
            "2:3",
            "5:4",
            "4:5",
            "21:9"
        ]