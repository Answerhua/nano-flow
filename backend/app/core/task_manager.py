"""Task Manager - In-memory task storage and status management"""

import asyncio
from typing import Dict, Any, Optional
from datetime import datetime
from uuid import uuid4
from loguru import logger

from ..schemas import TaskStatus, TaskResponse, GenerationResult, ErrorDetail, ImageMetadata


class TaskManager:
    """
    任务管理器 - 使用内存存储（简化版）
    
    在生产环境中应该使用 Redis 或数据库
    """
    
    def __init__(self):
        self._tasks: Dict[str, Dict[str, Any]] = {}
        self._lock = asyncio.Lock()
    
    async def create_task(
        self,
        title: str,
        input_data: Dict[str, Any]
    ) -> str:
        """
        创建新任务
        
        Args:
            title: 任务标题
            input_data: 输入数据
            
        Returns:
            任务 ID
        """
        task_id = str(uuid4())
        
        async with self._lock:
            self._tasks[task_id] = {
                "task_id": task_id,
                "title": title,
                "status": TaskStatus.PENDING,
                "progress": 0,
                "message": "任务已创建，等待处理...",
                "input_data": input_data,
                "result": None,
                "error": None,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "estimated_time": None
            }
        
        logger.info(f"Task created: {task_id}")
        return task_id
    
    async def update_status(
        self,
        task_id: str,
        status: TaskStatus,
        progress: Optional[int] = None,
        message: Optional[str] = None,
        estimated_time: Optional[int] = None
    ):
        """
        更新任务状态
        
        Args:
            task_id: 任务 ID
            status: 新状态
            progress: 进度（0-100）
            message: 状态消息
            estimated_time: 预计剩余时间（秒）
        """
        async with self._lock:
            if task_id not in self._tasks:
                logger.error(f"Task not found: {task_id}")
                return
            
            task = self._tasks[task_id]
            task["status"] = status
            task["updated_at"] = datetime.now().isoformat()
            
            if progress is not None:
                task["progress"] = progress
            
            if message is not None:
                task["message"] = message
            
            if estimated_time is not None:
                task["estimated_time"] = estimated_time
        
        logger.info(f"Task {task_id} updated: {status} ({progress}%)")
    
    async def set_result(
        self,
        task_id: str,
        image_url: str,
        thumbnail_url: str,
        enhanced_prompt: str,
        metadata: Dict[str, Any]
    ):
        """
        设置任务结果
        
        Args:
            task_id: 任务 ID
            image_url: 图片 URL
            thumbnail_url: 缩略图 URL
            enhanced_prompt: 增强后的提示词
            metadata: 元数据
        """
        async with self._lock:
            if task_id not in self._tasks:
                logger.error(f"Task not found: {task_id}")
                return
            
            task = self._tasks[task_id]
            task["status"] = TaskStatus.COMPLETED
            task["progress"] = 100
            task["message"] = "生成完成！ ✨"
            task["result"] = {
                "image_url": image_url,
                "thumbnail_url": thumbnail_url,
                "enhanced_prompt": enhanced_prompt,
                "metadata": metadata
            }
            task["updated_at"] = datetime.now().isoformat()
        
        logger.info(f"Task {task_id} completed successfully")
    
    async def set_error(
        self,
        task_id: str,
        error_code: str,
        error_message: str
    ):
        """
        设置任务错误
        
        Args:
            task_id: 任务 ID
            error_code: 错误代码
            error_message: 错误消息
        """
        async with self._lock:
            if task_id not in self._tasks:
                logger.error(f"Task not found: {task_id}")
                return
            
            task = self._tasks[task_id]
            task["status"] = TaskStatus.FAILED
            task["message"] = "生成失败"
            task["error"] = {
                "code": error_code,
                "message": error_message
            }
            task["updated_at"] = datetime.now().isoformat()
        
        logger.error(f"Task {task_id} failed: {error_code} - {error_message}")
    
    async def get_task(self, task_id: str) -> Optional[TaskResponse]:
        """
        获取任务状态
        
        Args:
            task_id: 任务 ID
            
        Returns:
            任务响应对象，如果不存在返回 None
        """
        async with self._lock:
            if task_id not in self._tasks:
                return None
            
            task = self._tasks[task_id].copy()
        
        # 构建响应对象
        result = None
        if task["result"]:
            result = GenerationResult(
                image_url=task["result"]["image_url"],
                thumbnail_url=task["result"]["thumbnail_url"],
                enhanced_prompt=task["result"]["enhanced_prompt"],
                metadata=ImageMetadata(**task["result"]["metadata"])
            )
        
        error = None
        if task["error"]:
            error = ErrorDetail(
                code=task["error"]["code"],
                message=task["error"]["message"]
            )
        
        return TaskResponse(
            task_id=task["task_id"],
            status=task["status"],
            progress=task.get("progress"),
            message=task["message"],
            result=result,
            error=error,
            estimated_time=task.get("estimated_time")
        )
    
    async def delete_task(self, task_id: str):
        """
        删除任务
        
        Args:
            task_id: 任务 ID
        """
        async with self._lock:
            if task_id in self._tasks:
                del self._tasks[task_id]
                logger.info(f"Task deleted: {task_id}")
    
    async def get_all_tasks(self) -> Dict[str, Any]:
        """
        获取所有任务（调试用）
        
        Returns:
            所有任务的字典
        """
        async with self._lock:
            return self._tasks.copy()
    
    async def cleanup_old_tasks(self, max_age_hours: int = 24):
        """
        清理旧任务
        
        Args:
            max_age_hours: 最大保留时间（小时）
        """
        from datetime import timedelta
        
        cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
        
        async with self._lock:
            tasks_to_delete = []
            for task_id, task in self._tasks.items():
                created_at = datetime.fromisoformat(task["created_at"])
                if created_at < cutoff_time:
                    tasks_to_delete.append(task_id)
            
            for task_id in tasks_to_delete:
                del self._tasks[task_id]
            
            if tasks_to_delete:
                logger.info(f"Cleaned up {len(tasks_to_delete)} old tasks")


# 全局单例
task_manager = TaskManager()
