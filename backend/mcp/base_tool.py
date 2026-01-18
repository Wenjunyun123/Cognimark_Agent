"""
MCP工具基类和接口定义

定义统一的工具接口，所有工具都必须继承BaseTool
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from enum import Enum


class ToolStatus(Enum):
    """工具执行状态"""
    SUCCESS = "success"
    ERROR = "error"
    TIMEOUT = "timeout"


@dataclass
class ToolResult:
    """
    工具执行结果

    Attributes:
        success: 是否成功
        status: 状态
        data: 返回数据
        error: 错误信息（如果有）
        metadata: 元数据
    """
    success: bool
    status: ToolStatus
    data: Any = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "success": self.success,
            "status": self.status.value,
            "data": self.data,
            "error": self.error,
            "metadata": self.metadata,
        }


@dataclass
class ToolParameter:
    """
    工具参数定义

    Attributes:
        name: 参数名
        type: 参数类型
        description: 参数描述
        required: 是否必需
        default: 默认值
    """
    name: str
    type: str
    description: str
    required: bool = True
    default: Any = None


class ToolError(Exception):
    """工具执行错误"""

    def __init__(self, message: str, tool_name: str = "", details: Dict = None):
        self.message = message
        self.tool_name = tool_name
        self.details = details or {}
        super().__init__(f"[{tool_name}] {message}")


class BaseTool(ABC):
    """
    工具基类

    所有MCP工具都必须继承这个类并实现execute方法
    """

    # 工具基本信息（子类必须设置）
    name: str = ""
    description: str = ""
    version: str = "1.0.0"

    def __init__(self):
        if not self.name:
            raise ValueError(f"{self.__class__.__name__} must define 'name' attribute")
        if not self.description:
            raise ValueError(f"{self.__class__.__name__} must define 'description' attribute")

    @property
    def parameters(self) -> List[ToolParameter]:
        """
        定义工具参数

        Returns:
            List[ToolParameter]: 参数列表
        """
        return []

    def validate_parameters(self, params: Dict[str, Any]) -> bool:
        """
        验证参数

        Args:
            params: 输入参数

        Returns:
            bool: 是否有效

        Raises:
            ToolError: 参数验证失败
        """
        # 检查必需参数
        for param in self.parameters:
            if param.required and param.name not in params:
                raise ToolError(
                    f"Missing required parameter: {param.name}",
                    tool_name=self.name
                )

        # 检查参数类型
        for param in self.parameters:
            if param.name in params:
                value = params[param.name]
                expected_type = param.type

                # 简单类型检查
                if expected_type == "str" and not isinstance(value, str):
                    raise ToolError(
                        f"Parameter '{param.name}' must be string",
                        tool_name=self.name
                    )
                elif expected_type == "int" and not isinstance(value, int):
                    raise ToolError(
                        f"Parameter '{param.name}' must be integer",
                        tool_name=self.name
                    )
                elif expected_type == "float" and not isinstance(value, (int, float)):
                    raise ToolError(
                        f"Parameter '{param.name}' must be number",
                        tool_name=self.name
                    )
                elif expected_type == "bool" and not isinstance(value, bool):
                    raise ToolError(
                        f"Parameter '{param.name}' must be boolean",
                        tool_name=self.name
                    )

        return True

    @abstractmethod
    def execute(self, **kwargs) -> ToolResult:
        """
        执行工具

        Args:
            **kwargs: 工具参数

        Returns:
            ToolResult: 执行结果

        Raises:
            ToolError: 执行失败
        """
        pass

    def get_info(self) -> Dict[str, Any]:
        """
        获取工具信息

        Returns:
            Dict: 工具信息
        """
        return {
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "parameters": [
                {
                    "name": p.name,
                    "type": p.type,
                    "description": p.description,
                    "required": p.required,
                    "default": p.default,
                }
                for p in self.parameters
            ],
        }

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name='{self.name}')"
