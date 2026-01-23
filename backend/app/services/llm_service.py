"""LLM Service for prompt enhancement using Qwen"""

import httpx
from typing import Dict, Any, List
from loguru import logger

from ..config import settings


class LLMService:
    """千问 LLM 服务，用于提示词增强和智能填充"""
    
    def __init__(self):
        self.api_key = settings.QWEN_API_KEY
        self.api_base = settings.QWEN_API_BASE
        self.model = settings.LLM_MODEL
        self.temperature = settings.LLM_TEMPERATURE
        self.max_tokens = settings.LLM_MAX_TOKENS
        
    async def enhance_step_description(
        self,
        title: str,
        description: str,
        character_type: str,
        color_scheme: str
    ) -> str:
        """
        使用 LLM 增强单个步骤的视觉描述
        
        Args:
            title: 步骤标题
            description: 步骤描述
            character_type: 角色类型（bear, cat, rabbit等）
            color_scheme: 配色方案
            
        Returns:
            增强后的视觉描述
        """
        prompt = self._build_enhancement_prompt(
            title, description, character_type, color_scheme
        )
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.api_base}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.model,
                        "messages": [
                            {
                                "role": "system",
                                "content": "你是一个专业的视觉描述专家，擅长将流程步骤转化为生动的可视化场景描述。"
                            },
                            {
                                "role": "user",
                                "content": prompt
                            }
                        ],
                        "temperature": self.temperature,
                        "max_tokens": self.max_tokens
                    }
                )
                
                response.raise_for_status()
                result = response.json()
                
                enhanced = result["choices"][0]["message"]["content"].strip()
                logger.info(f"Enhanced step: {title} -> {enhanced[:50]}...")
                return enhanced
                
        except Exception as e:
            logger.error(f"LLM enhancement failed: {e}")
            # 降级：返回原始描述
            return f"{title}: {description}"
    
    def _build_enhancement_prompt(
        self,
        title: str,
        description: str,
        character_type: str,
        color_scheme: str
    ) -> str:
        """构建增强提示词"""
        return f"""请将以下流程步骤转化为适合图像生成的视觉描述：

步骤标题：{title}
步骤描述：{description}
角色类型：{character_type}
配色方案：{color_scheme}

要求：
1. 描述要简洁生动，适合文生图模型理解
2. 融入 {character_type} 角色元素（如果不是 random）
3. 使用 {color_scheme} 配色相关的关键词
4. 突出动作和关键物品
5. 使用英文输出，适合 SD/DALL-E 等模型
6. 保持可爱（kawaii）和扁平化（flat）风格

示例输出格式：
"A cute {character_type} character holding [tool/item], performing [action], {color_scheme} color palette, kawaii style, flat vector illustration"

请直接输出视觉描述，不要包含其他解释："""
    
    async def enhance_full_prompt(
        self,
        title: str,
        enhanced_steps: List[str],
        character_type: str,
        color_scheme: str,
        custom_tags: List[str]
    ) -> Dict[str, Any]:
        """
        整合所有步骤，生成完整的图像生成提示词
        
        Args:
            title: 流程图标题
            enhanced_steps: 增强后的步骤描述列表
            character_type: 角色类型
            color_scheme: 配色方案
            custom_tags: 自定义标签
            
        Returns:
            包含 enhanced_prompt 和 metadata 的字典
        """
        steps_text = "\n".join([f"{i+1}. {step}" for i, step in enumerate(enhanced_steps)])
        step_count = len(enhanced_steps)
        
        # 根据步骤数量选择布局
        layout = "horizontal timeline" if step_count <= 4 else "grid layout 2x3"
        
        # 构建基础提示词
        base_prompt = f"""Process infographic: "{title}"

Layout: {layout}
Style: Kawaii flat vector illustration
Character: {character_type if character_type != 'random' else 'cute animal character'}
Color scheme: {color_scheme}

Steps:
{steps_text}

Visual elements:
- Numbered circles or badges for each step
- Connecting arrows or lines between steps
- Clean white background
- Soft drop shadows
- Minimalist icons
"""
        
        # 添加自定义标签
        if custom_tags:
            tags_text = ", ".join(custom_tags)
            base_prompt += f"\nAdditional tags: {tags_text}"
        
        # 添加质量提示词
        quality_prompt = """

Quality tags: masterpiece, best quality, highly detailed, clean composition, professional infographic, modern design, 4k resolution"""
        
        # 添加负面提示词（虽然这里不直接使用，但可以记录）
        negative_prompt = "blurry, low quality, distorted, messy, cluttered, realistic photo, 3d render, ugly, duplicate"
        
        full_prompt = base_prompt + quality_prompt
        
        return {
            "enhanced_prompt": full_prompt.strip(),
            "negative_prompt": negative_prompt,
            "tokens_used": len(full_prompt) // 4,  # 粗略估算
            "llm_model": self.model
        }
    
    async def smart_fill_steps(
        self,
        topic: str,
        step_count: int,
        language: str = "zh"
    ) -> Dict[str, Any]:
        """
        智能填充功能：根据主题生成流程步骤
        
        Args:
            topic: 主题
            step_count: 需要生成的步骤数量
            language: 语言（zh/en）
            
        Returns:
            包含 title 和 steps 的字典
        """
        prompt = self._build_smart_fill_prompt(topic, step_count, language)
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.api_base}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.model,
                        "messages": [
                            {
                                "role": "system",
                                "content": "你是一个专业的流程设计专家，擅长分解复杂任务为清晰的步骤。"
                            },
                            {
                                "role": "user",
                                "content": prompt
                            }
                        ],
                        "temperature": 0.7,
                        "max_tokens": 800
                    }
                )
                
                response.raise_for_status()
                result = response.json()
                
                content = result["choices"][0]["message"]["content"].strip()
                logger.info(f"Smart fill result: {content[:100]}...")
                
                # 解析 LLM 返回的结构化数据
                return self._parse_smart_fill_response(content, step_count)
                
        except Exception as e:
            logger.error(f"Smart fill failed: {e}")
            raise
    
    def _build_smart_fill_prompt(self, topic: str, step_count: int, language: str) -> str:
        """构建智能填充提示词"""
        lang_instruction = "中文" if language == "zh" else "English"
        
        return f"""请为以下主题生成一个清晰的流程步骤：

主题：{topic}
步骤数量：{step_count}
语言：{lang_instruction}

要求：
1. 生成 {step_count} 个步骤
2. 每个步骤包含标题（10-20字）和描述（20-50字）
3. 步骤要符合逻辑顺序
4. 描述要具体可操作
5. 适合制作成流程图

请按以下 JSON 格式输出（不要包含其他文字）：
{{
  "title": "流程图标题",
  "steps": [
    {{"title": "步骤1标题", "description": "步骤1描述"}},
    {{"title": "步骤2标题", "description": "步骤2描述"}}
  ]
}}"""
    
    def _parse_smart_fill_response(self, content: str, expected_count: int) -> Dict[str, Any]:
        """解析 LLM 返回的智能填充结果"""
        import json
        
        try:
            # 尝试提取 JSON
            start = content.find('{')
            end = content.rfind('}') + 1
            
            if start >= 0 and end > start:
                json_str = content[start:end]
                data = json.loads(json_str)
                
                # 验证结构
                if "title" in data and "steps" in data:
                    # 确保步骤数量正确
                    steps = data["steps"][:expected_count]
                    return {
                        "title": data["title"],
                        "steps": steps
                    }
            
            raise ValueError("Invalid JSON structure")
            
        except Exception as e:
            logger.error(f"Failed to parse smart fill response: {e}")
            # 降级：返回默认结构
            return {
                "title": "流程步骤",
                "steps": [
                    {"title": f"步骤 {i+1}", "description": "请填写描述"}
                    for i in range(expected_count)
                ]
            }
