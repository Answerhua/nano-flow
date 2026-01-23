"""Generation API endpoints"""

import asyncio
from fastapi import APIRouter, HTTPException, BackgroundTasks
from loguru import logger

from ...schemas import GenerateRequest, GenerateResponse, TaskResponse
from ...services import PromptBuilder, ImageGenerator
from ...core.task_manager import task_manager

router = APIRouter(prefix="/generate", tags=["generate"])


@router.post("", response_model=GenerateResponse)
async def create_generation(
    request: GenerateRequest,
    background_tasks: BackgroundTasks
):
    """
    创建图像生成任务
    
    接收用户输入，创建异步生成任务，立即返回 task_id
    """
    try:
        # 创建任务
        task_id = await task_manager.create_task(
            title=request.title,
            input_data=request.model_dump()
        )
        
        # 在后台执行生成任务
        background_tasks.add_task(
            generate_image_task,
            task_id=task_id,
            request=request
        )
        
        logger.info(f"Generation task created: {task_id}")
        
        return GenerateResponse(
            task_id=task_id,
            status="processing",
            message="正在分析需求... 🧠"
        )
        
    except Exception as e:
        logger.error(f"Failed to create generation task: {e}")
        raise HTTPException(status_code=500, detail=f"创建任务失败: {str(e)}")


@router.get("/{task_id}", response_model=TaskResponse)
async def get_generation_status(task_id: str):
    """
    查询生成任务状态
    
    客户端轮询此接口获取任务进度和结果
    """
    try:
        task = await task_manager.get_task(task_id)
        
        if task is None:
            raise HTTPException(status_code=404, detail="任务不存在")
        
        return task
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get task status: {e}")
        raise HTTPException(status_code=500, detail=f"查询任务失败: {str(e)}")


async def generate_image_task(task_id: str, request: GenerateRequest):
    """
    后台任务：执行图像生成
    
    流程：
    1. 更新状态：开始处理
    2. 构建提示词（使用 LLM）
    3. 调用 Nano Banana Pro 生成图像
    4. 创建缩略图
    5. 更新状态：完成
    """
    try:
        # Step 1: 开始处理
        await task_manager.update_status(
            task_id=task_id,
            status="processing",
            progress=10,
            message="正在分析需求... 🧠",
            estimated_time=60
        )
        
        # Step 2: 构建提示词
        logger.info(f"Task {task_id}: Building prompt...")
        prompt_builder = PromptBuilder()
        
        prompt_result = await prompt_builder.build_prompt(
            title=request.title,
            steps=request.steps,
            visual_prefs=request.visual_preferences
        )
        
        enhanced_prompt = prompt_result["enhanced_prompt"]
        negative_prompt = prompt_builder.get_negative_prompt()
        
        await task_manager.update_status(
            task_id=task_id,
            status="processing",
            progress=40,
            message="正在绘制可爱的角色... 🎨",
            estimated_time=40
        )
        
        # Step 3: 生成图像
        logger.info(f"Task {task_id}: Generating image...")
        image_generator = ImageGenerator()
        
        generation_result = await image_generator.generate_image(
            prompt=enhanced_prompt,
            negative_prompt=negative_prompt,
            seed=request.seed
        )
        
        await task_manager.update_status(
            task_id=task_id,
            status="processing",
            progress=80,
            message="正在优化画面... ✨",
            estimated_time=10
        )
        
        # Step 4: 创建缩略图
        logger.info(f"Task {task_id}: Creating thumbnail...")
        thumbnail_url = await image_generator.create_thumbnail(
            image_url=generation_result["image_url"]
        )
        
        # Step 5: 完成
        await task_manager.set_result(
            task_id=task_id,
            image_url=generation_result["image_url"],
            thumbnail_url=thumbnail_url,
            enhanced_prompt=enhanced_prompt,
            metadata={
                "resolution": f"{generation_result['width']}x{generation_result['height']}",
                "seed": generation_result["seed"],
                "model_version": generation_result["model"],
                "cfg_scale": generation_result["cfg_scale"],
                "sampling_steps": generation_result["steps"]
            }
        )
        
        logger.info(f"Task {task_id}: Completed successfully")
        
    except Exception as e:
        logger.error(f"Task {task_id} failed: {e}")
        await task_manager.set_error(
            task_id=task_id,
            error_code="GENERATION_ERROR",
            error_message=str(e)
        )
