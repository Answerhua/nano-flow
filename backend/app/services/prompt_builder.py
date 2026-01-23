"""Prompt Builder - Core Brain for converting user input to image prompts"""

from typing import List, Dict, Any
from loguru import logger

from ..schemas import StepItem, VisualPreferences, CharacterType, ColorScheme
from .llm_service import LLMService


class PromptBuilder:
    """
    提示词构造器 - 核心 Brain
    负责将用户输入转换为高质量的图像生成提示词
    """
    
    def __init__(self):
        self.llm_service = LLMService()
    
    async def build_prompt(
        self,
        title: str,
        steps: List[StepItem],
        visual_prefs: VisualPreferences
    ) -> Dict[str, Any]:
        """
        构建完整的图像生成提示词
        
        流程：
        1. 解析视觉偏好
        2. 使用 LLM 增强每个步骤的描述
        3. 组装最终提示词
        4. 添加质量和风格标签
        
        Args:
            title: 流程图标题
            steps: 步骤列表
            visual_prefs: 视觉偏好
            
        Returns:
            包含 enhanced_prompt, negative_prompt 等的字典
        """
        logger.info(f"Building prompt for: {title} with {len(steps)} steps")
        
        # 1. 解析视觉偏好
        character = self._resolve_character(visual_prefs.character)
        color_scheme = self._resolve_color_scheme(visual_prefs.color_scheme)
        
        # 2. 使用 LLM 增强每个步骤
        enhanced_steps = []
        for i, step in enumerate(steps):
            try:
                enhanced = await self.llm_service.enhance_step_description(
                    title=step.title,
                    description=step.description,
                    character_type=character,
                    color_scheme=color_scheme
                )
                enhanced_steps.append(enhanced)
            except Exception as e:
                logger.error(f"Failed to enhance step {i}: {e}")
                # 降级：使用简单格式
                enhanced_steps.append(
                    f"A {character} character {step.title.lower()}: {step.description}"
                )
        
        # 3. 组装最终提示词
        result = await self.llm_service.enhance_full_prompt(
            title=title,
            enhanced_steps=enhanced_steps,
            character_type=character,
            color_scheme=color_scheme,
            custom_tags=visual_prefs.custom_tags
        )
        
        logger.info(f"Prompt built successfully, tokens: {result.get('tokens_used', 0)}")
        return result
    
    def build_simple_prompt(
        self,
        title: str,
        steps: List[StepItem],
        visual_prefs: VisualPreferences
    ) -> str:
        """
        构建简单提示词（不使用 LLM，用于降级场景）
        
        Args:
            title: 流程图标题
            steps: 步骤列表
            visual_prefs: 视觉偏好
            
        Returns:
            简单的提示词字符串
        """
        character = self._resolve_character(visual_prefs.character)
        color_scheme = self._resolve_color_scheme(visual_prefs.color_scheme)
        
        step_count = len(steps)
        layout = "horizontal timeline" if step_count <= 4 else "grid layout"
        
        # 构建步骤描述
        steps_text = []
        for i, step in enumerate(steps):
            steps_text.append(f"{i+1}. {step.title}: {step.description}")
        
        prompt = f"""Process infographic: "{title}"

{layout} with {step_count} steps:
{chr(10).join(steps_text)}

Style: Kawaii flat vector illustration with {character} character
Color scheme: {color_scheme}
Clean white background, numbered badges, connecting arrows
Minimalist design, soft shadows, professional infographic

Quality: masterpiece, best quality, highly detailed, 4k resolution"""
        
        # 添加自定义标签
        if visual_prefs.custom_tags:
            prompt += f"\nTags: {', '.join(visual_prefs.custom_tags)}"
        
        return prompt
    
    def _resolve_character(self, character: CharacterType) -> str:
        """解析角色类型"""
        if character == CharacterType.RANDOM:
            import random
            characters = [
                CharacterType.BEAR,
                CharacterType.CAT,
                CharacterType.RABBIT,
                CharacterType.DOG,
                CharacterType.PANDA
            ]
            character = random.choice(characters)
        
        character_map = {
            CharacterType.BEAR: "white bear",
            CharacterType.CAT: "orange cat",
            CharacterType.RABBIT: "pink rabbit",
            CharacterType.DOG: "brown dog",
            CharacterType.PANDA: "panda"
        }
        
        return character_map.get(character, "cute animal")
    
    def _resolve_color_scheme(self, color_scheme: ColorScheme) -> str:
        """解析配色方案"""
        if color_scheme == ColorScheme.RANDOM:
            import random
            schemes = [
                ColorScheme.PASTEL,
                ColorScheme.TECH_BLUE,
                ColorScheme.WARM_ORANGE,
                ColorScheme.MINT_GREEN,
                ColorScheme.PINK_PURPLE
            ]
            color_scheme = random.choice(schemes)
        
        scheme_map = {
            ColorScheme.PASTEL: "pastel colors (soft pink, baby blue, mint green, lavender)",
            ColorScheme.TECH_BLUE: "tech blue gradient (blue, cyan, purple)",
            ColorScheme.WARM_ORANGE: "warm colors (orange, coral, peach, yellow)",
            ColorScheme.MINT_GREEN: "mint green palette (mint, teal, sage, lime)",
            ColorScheme.PINK_PURPLE: "pink purple gradient (pink, magenta, purple, violet)"
        }
        
        return scheme_map.get(color_scheme, "pastel colors")
    
    def get_negative_prompt(self) -> str:
        """获取通用的负面提示词"""
        return (
            "blurry, low quality, distorted, messy, cluttered, "
            "realistic photo, 3d render, ugly, duplicate, watermark, "
            "text errors, bad anatomy, extra limbs, poorly drawn, "
            "deformed, mutation, disfigured, bad proportions"
        )
    
    def estimate_complexity(self, steps: List[StepItem]) -> str:
        """
        评估提示词复杂度
        
        Returns:
            "simple", "medium", "complex"
        """
        step_count = len(steps)
        total_text_length = sum(len(step.title) + len(step.description) for step in steps)
        
        if step_count <= 3 and total_text_length < 200:
            return "simple"
        elif step_count <= 4 and total_text_length < 400:
            return "medium"
        else:
            return "complex"
