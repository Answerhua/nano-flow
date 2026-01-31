"""Generation API endpoints"""

import asyncio
from fastapi import APIRouter, HTTPException, BackgroundTasks
from loguru import logger

from ...schemas import (
    GenerateRequest, 
    GenerateResponse, 
    TaskResponse,
    GenerateStepsRequest,
    GenerateStepsResponse
)
from ...services import PromptBuilder, ImageGenerator
from ...services.llm_service import LLMService
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


@router.post("/generate-steps", response_model=GenerateStepsResponse)
async def generate_steps(request: GenerateStepsRequest):
    """
    根据主题自动生成步骤列表
    
    此接口调用千问 API，根据用户输入的主题自动生成 3-6 个流程步骤。
    生成的步骤可以直接用于 /api/v1/generate 接口。
    """
    try:
        logger.info(f"Generating steps for topic: {request.title}")
        
        # 创建 LLM 服务实例
        llm_service = LLMService()
        
        # 调用 LLM 生成步骤
        steps = await llm_service.generate_steps_from_topic(request.title)
        
        logger.info(f"Successfully generated {len(steps)} steps")
        
        return GenerateStepsResponse(steps=steps)
        
    except ValueError as e:
        # JSON 解析失败或格式错误
        logger.error(f"Failed to parse LLM response: {e}")
        raise HTTPException(
            status_code=422,
            detail=f"解析 AI 响应失败: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Failed to generate steps: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"生成步骤失败: {str(e)}"
        )
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
        
        # 定义进度回调函数
        async def progress_callback(progress: int, status: str):
            """GRSAI 进度回调"""
            message_map = {
                0: "开始生成图像... 🎨",
                20: "正在理解提示词... 🧠",
                40: "正在绘制基础轮廓... ✏️",
                60: "正在添加细节... 🖌️",
                80: "正在优化画面... ✨",
                100: "即将完成... 🎉"
            }
            
            # 根据进度选择消息
            message = message_map.get(progress, f"生成中... {progress}%")
            
            # 估算剩余时间（假设总共需要 60 秒）
            estimated_time = max(0, int((100 - progress) * 0.6))
            
            await task_manager.update_status(
                task_id=task_id,
                status="processing",
                progress=40 + int(progress * 0.4),  # 40-80% 的进度范围
                message=message,
                estimated_time=estimated_time
            )
        
        generation_result = await image_generator.generate_image(
            prompt=enhanced_prompt,
            negative_prompt=negative_prompt,
            seed=request.seed,
            progress_callback=progress_callback
        )
        
        await task_manager.update_status(
            task_id=task_id,
            status="processing",
            progress=85,
            message="正在优化画面... ✨",
            estimated_time=5
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


