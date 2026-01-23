"""
技能基类 - 参考LangChain的Chain设计

每个技能是一个可执行的单元，可以：
1. 调用MCP工具
2. 使用LLM进行推理
3. 与其他技能组合
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from enum import Enum


class SkillStatus(Enum):
    """技能执行状态"""
    SUCCESS = "success"
    ERROR = "error"
    PARTIAL = "partial"


@dataclass
class SkillContext:
    """
    技能执行上下文（类似LangChain的Memory）

    在技能之间传递数据和状态
    """
    inputs: Dict[str, Any] = field(default_factory=dict)
    outputs: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    intermediate_steps: List[Dict[str, Any]] = field(default_factory=list)

    def update(self, key: str, value: Any) -> None:
        """更新上下文"""
        self.outputs[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        """获取上下文值"""
        return self.outputs.get(key, self.inputs.get(key, default))

    def add_step(self, step_name: str, step_data: Any) -> None:
        """添加中间步骤"""
        self.intermediate_steps.append({
            "step": step_name,
            "data": step_data,
        })


@dataclass
class SkillResult:
    """
    技能执行结果（类似LangChain的Chain Output）
    """
    success: bool
    status: SkillStatus
    output: Any = None
    context: Optional[SkillContext] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "success": self.success,
            "status": self.status.value,
            "output": self.output,
            "error": self.error,
            "metadata": self.metadata,
        }


class BaseSkill(ABC):
    """
    技能基类（参考LangChain的Chain）

    设计原则：
    1. 每个技能完成一个特定任务
    2. 技能可以调用工具和LLM
    3. 技能可以组合形成更复杂的技能
    4. 技能维护自己的执行上下文
    """

    # 技能基本信息
    name: str = ""
    description: str = ""
    version: str = "1.0.0"

    # 依赖的工具和LLM
    required_tools: List[str] = []  # 需要的MCP工具名称
    required_llm: bool = False  # 是否需要LLM

    def __init__(self, tool_manager=None, llm_service=None):
        """
        初始化技能

        Args:
            tool_manager: MCP工具管理器
            llm_service: LLM服务
        """
        if not self.name:
            raise ValueError(f"{self.__class__.__name__} must define 'name' attribute")
        if not self.description:
            raise ValueError(f"{self.__class__.__name__} must define 'description' attribute")

        self.tool_manager = tool_manager
        self.llm_service = llm_service

        # 延迟验证依赖（在execute时验证）
        # self._validate_dependencies()

    def _validate_dependencies(self) -> None:
        """验证技能的依赖是否满足"""
        if self.required_tools and not self.tool_manager:
            raise ValueError(
                f"Skill '{self.name}' requires tools but no tool_manager provided"
            )

        if self.required_llm and not self.llm_service:
            raise ValueError(
                f"Skill '{self.name}' requires LLM but no llm_service provided"
            )

        # 检查所需工具是否已注册
        if self.tool_manager and self.required_tools:
            available_tools = self.tool_manager.list_tools()
            for tool_name in self.required_tools:
                if tool_name not in available_tools:
                    raise ValueError(
                        f"Skill '{self.name}' requires tool '{tool_name}' which is not registered"
                    )

    @abstractmethod
    def execute(
        self,
        inputs: Dict[str, Any],
        context: Optional[SkillContext] = None
    ) -> SkillResult:
        """
        执行技能（类似LangChain的__call__）

        Args:
            inputs: 输入参数
            context: 执行上下文

        Returns:
            SkillResult: 执行结果
        """
        pass

    def run(self, **kwargs) -> SkillResult:
        """
        便捷方法：直接执行技能

        Args:
            **kwargs: 输入参数

        Returns:
            SkillResult: 执行结果
        """
        return self.execute(kwargs)

    def compose(self, *skills: 'BaseSkill') -> 'CompositeSkill':
        """
        组合多个技能（类似LangChain的SequentialChain）

        Args:
            *skills: 要组合的技能

        Returns:
            CompositeSkill: 组合技能
        """
        return CompositeSkill(self, *skills)

    def get_info(self) -> Dict[str, Any]:
        """获取技能信息"""
        return {
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "required_tools": self.required_tools,
            "required_llm": self.required_llm,
        }

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name='{self.name}')"


class CompositeSkill(BaseSkill):
    """
    组合技能（类似LangChain的SequentialChain）

    将多个技能串联执行，前一个技能的输出作为后一个技能的输入
    """

    name = "composite"
    description = "组合多个技能顺序执行"
    required_tools = []
    required_llm = False

    def __init__(self, *skills: BaseSkill, tool_manager=None, llm_service=None):
        """
        初始化组合技能

        Args:
            *skills: 要组合的技能
            tool_manager: 工具管理器
            llm_service: LLM服务
        """
        self.skills = skills
        self.name = f"composite_{'_'.join(s.name for s in skills)}"
        super().__init__(tool_manager, llm_service)

    def execute(
        self,
        inputs: Dict[str, Any],
        context: Optional[SkillContext] = None
    ) -> SkillResult:
        """
        顺序执行所有技能

        Args:
            inputs: 初始输入
            context: 执行上下文

        Returns:
            SkillResult: 最终执行结果
        """
        if context is None:
            context = SkillContext(inputs=inputs)

        # 初始化输入
        current_inputs = inputs

        try:
            # 顺序执行每个技能
            for i, skill in enumerate(self.skills):
                context.add_step(f"skill_{i}_{skill.name}", current_inputs)

                # 执行技能
                result = skill.execute(current_inputs, context)

                if not result.success:
                    return SkillResult(
                        success=False,
                        status=SkillStatus.ERROR,
                        error=f"Skill '{skill.name}' failed: {result.error}",
                        context=context,
                    )

                # 将输出作为下一个技能的输入
                current_inputs = result.output if isinstance(result.output, dict) else {"result": result.output}

            return SkillResult(
                success=True,
                status=SkillStatus.SUCCESS,
                output=current_inputs,
                context=context,
                metadata={
                    "skills_executed": len(self.skills),
                    "steps": len(context.intermediate_steps),
                },
            )

        except Exception as e:
            return SkillResult(
                success=False,
                status=SkillStatus.ERROR,
                error=str(e),
                context=context,
            )
