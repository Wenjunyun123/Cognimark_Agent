"""
技能管理器 - 参考LangChain的设计

负责技能的注册、发现和执行
"""
from typing import Dict, List, Any, Optional
import logging

from .base_skill import BaseSkill, SkillResult, SkillContext, CompositeSkill


# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SkillManager:
    """
    技能管理器（类似LangChain的执行器）

    功能：
    1. 技能注册和发现
    2. 技能执行
    3. 技能组合
    4. 依赖注入
    """

    def __init__(self, tool_manager=None, llm_service=None):
        """
        初始化技能管理器

        Args:
            tool_manager: MCP工具管理器
            llm_service: LLM服务
        """
        self.skills: Dict[str, BaseSkill] = {}
        self.tool_manager = tool_manager
        self.llm_service = llm_service
        self.logger = logger

    def register_skill(self, skill: BaseSkill) -> None:
        """
        注册技能

        Args:
            skill: 技能实例

        Raises:
            ValueError: 技能名已存在
        """
        if skill.name in self.skills:
            raise ValueError(f"Skill '{skill.name}' already registered")

        # 注入依赖
        if skill.tool_manager is None and self.tool_manager:
            skill.tool_manager = self.tool_manager
        if skill.llm_service is None and self.llm_service:
            skill.llm_service = self.llm_service

        self.skills[skill.name] = skill
        self.logger.info(f"Registered skill: {skill.name}")

    def unregister_skill(self, skill_name: str) -> bool:
        """
        注销技能

        Args:
            skill_name: 技能名

        Returns:
            bool: 是否成功
        """
        if skill_name in self.skills:
            del self.skills[skill_name]
            self.logger.info(f"Unregistered skill: {skill_name}")
            return True
        return False

    def get_skill(self, skill_name: str) -> Optional[BaseSkill]:
        """
        获取技能

        Args:
            skill_name: 技能名

        Returns:
            Optional[BaseSkill]: 技能实例，不存在则返回None
        """
        return self.skills.get(skill_name)

    def list_skills(self) -> List[str]:
        """
        列出所有技能名

        Returns:
            List[str]: 技能名列表
        """
        return list(self.skills.keys())

    def get_skills_info(self) -> List[Dict[str, Any]]:
        """
        获取所有技能的信息

        Returns:
            List[Dict]: 技能信息列表
        """
        return [skill.get_info() for skill in self.skills.values()]

    def execute_skill(
        self,
        skill_name: str,
        inputs: Dict[str, Any],
        context: Optional[SkillContext] = None,
    ) -> SkillResult:
        """
        执行单个技能

        Args:
            skill_name: 技能名
            inputs: 输入参数
            context: 执行上下文

        Returns:
            SkillResult: 执行结果

        Raises:
            ValueError: 技能不存在
        """
        skill = self.get_skill(skill_name)
        if not skill:
            raise ValueError(f"Skill '{skill_name}' not found")

        self.logger.info(f"Executing skill: {skill_name} with inputs: {list(inputs.keys())}")
        result = skill.execute(inputs, context)

        self.logger.info(
            f"Skill {skill_name} completed: "
            f"{'success' if result.success else 'failed'}"
        )

        return result

    def execute_skill_chain(
        self,
        skill_names: List[str],
        initial_inputs: Dict[str, Any],
        context: Optional[SkillContext] = None,
    ) -> List[SkillResult]:
        """
        执行技能链

        Args:
            skill_names: 技能名列表（按执行顺序）
            initial_inputs: 初始输入
            context: 执行上下文

        Returns:
            List[SkillResult]: 每个技能的执行结果
        """
        if context is None:
            context = SkillContext(inputs=initial_inputs)

        results = []
        current_inputs = initial_inputs

        for skill_name in skill_names:
            result = self.execute_skill(skill_name, current_inputs, context)
            results.append(result)

            if not result.success:
                # 如果某个技能失败，停止执行
                self.logger.error(f"Skill chain stopped at {skill_name} due to error")
                break

            # 将输出作为下一个技能的输入
            current_inputs = result.output if isinstance(result.output, dict) else {"result": result.output}

        return results

    def create_composite_skill(
        self,
        *skill_names: str
    ) -> CompositeSkill:
        """
        创建组合技能

        Args:
            *skill_names: 要组合的技能名

        Returns:
            CompositeSkill: 组合技能实例

        Raises:
            ValueError: 某个技能不存在
        """
        skills = []
        for name in skill_names:
            skill = self.get_skill(name)
            if not skill:
                raise ValueError(f"Skill '{name}' not found")
            skills.append(skill)

        return CompositeSkill(*skills)

    def get_skills_description(self) -> str:
        """
        获取所有技能的描述（用于LLM Prompt）

        Returns:
            str: 格式化的技能描述
        """
        descriptions = []
        for skill in self.skills.values():
            info = skill.get_info()
            tool_desc = ", ".join(info["required_tools"]) if info["required_tools"] else "none"
            descriptions.append(
                f"- {info['name']}: {info['description']}\n"
                f"  Tools: {tool_desc}\n"
                f"  Requires LLM: {info['required_llm']}"
            )

        return "\n".join(descriptions)
