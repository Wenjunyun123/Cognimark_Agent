"""
工具管理器

负责工具的注册、发现、调用和执行
"""
from typing import Dict, List, Any, Optional
import logging

from .base_tool import BaseTool, ToolResult, ToolError, ToolStatus


# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ToolManager:
    """
    工具管理器

    功能：
    1. 工具注册和发现
    2. 工具调用
    3. 错误处理和重试
    4. 工具调用链
    """

    def __init__(self):
        """初始化工具管理器"""
        self.tools: Dict[str, BaseTool] = {}
        self.logger = logger

    def register_tool(self, tool: BaseTool) -> None:
        """
        注册工具

        Args:
            tool: 工具实例

        Raises:
            ValueError: 工具名已存在
        """
        if tool.name in self.tools:
            raise ValueError(f"Tool '{tool.name}' already registered")

        self.tools[tool.name] = tool
        self.logger.info(f"Registered tool: {tool.name}")

    def unregister_tool(self, tool_name: str) -> bool:
        """
        注销工具

        Args:
            tool_name: 工具名

        Returns:
            bool: 是否成功
        """
        if tool_name in self.tools:
            del self.tools[tool_name]
            self.logger.info(f"Unregistered tool: {tool_name}")
            return True
        return False

    def get_tool(self, tool_name: str) -> Optional[BaseTool]:
        """
        获取工具

        Args:
            tool_name: 工具名

        Returns:
            Optional[BaseTool]: 工具实例，不存在则返回None
        """
        return self.tools.get(tool_name)

    def list_tools(self) -> List[str]:
        """
        列出所有工具名

        Returns:
            List[str]: 工具名列表
        """
        return list(self.tools.keys())

    def get_tools_info(self) -> List[Dict[str, Any]]:
        """
        获取所有工具的信息

        Returns:
            List[Dict]: 工具信息列表
        """
        return [tool.get_info() for tool in self.tools.values()]

    def execute_tool(
        self,
        tool_name: str,
        **kwargs
    ) -> ToolResult:
        """
        执行单个工具

        Args:
            tool_name: 工具名
            **kwargs: 工具参数

        Returns:
            ToolResult: 执行结果

        Raises:
            ToolError: 工具不存在或执行失败
        """
        tool = self.get_tool(tool_name)
        if not tool:
            raise ToolError(
                f"Tool '{tool_name}' not found",
                tool_name=tool_name
            )

        try:
            # 验证参数
            tool.validate_parameters(kwargs)

            # 执行工具
            self.logger.info(f"Executing tool: {tool_name} with params: {kwargs}")
            result = tool.execute(**kwargs)

            self.logger.info(f"Tool {tool_name} executed successfully")
            return result

        except ToolError as e:
            self.logger.error(f"Tool {tool_name} execution failed: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error in tool {tool_name}: {e}")
            raise ToolError(
                f"Unexpected error: {str(e)}",
                tool_name=tool_name
            )

    def execute_tool_chain(
        self,
        chain: List[Dict[str, Any]],
        context: Optional[Dict[str, Any]] = None,
    ) -> List[ToolResult]:
        """
        执行工具调用链

        Args:
            chain: 工具链定义
                [
                    {"tool": "tool1", "params": {...}},
                    {"tool": "tool2", "params": {...}, "depends_on": ["tool1"]},
                ]
            context: 共享上下文

        Returns:
            List[ToolResult]: 每个工具的执行结果

        Raises:
            ToolError: 工具链执行失败
        """
        if context is None:
            context = {}

        results = []
        tool_outputs = {}  # 存储前序工具的输出

        for step in chain:
            tool_name = step.get("tool")
            params = step.get("params", {}).copy()
            depends_on = step.get("depends_on", [])

            # 检查依赖
            for dep in depends_on:
                if dep not in tool_outputs:
                    raise ToolError(
                        f"Dependency '{dep}' not found in previous outputs",
                        tool_name=tool_name
                    )

            # 将依赖工具的输出注入当前参数
            params.update(context)
            for dep in depends_on:
                if dep in tool_outputs:
                    params[f"_{dep}_output"] = tool_outputs[dep]

            # 执行工具
            result = self.execute_tool(tool_name, **params)
            results.append(result)
            tool_outputs[tool_name] = result.data

        return results

    def get_tools_description(self) -> str:
        """
        获取所有工具的描述（用于LLM Prompt）

        Returns:
            str: 格式化的工具描述
        """
        descriptions = []
        for tool in self.tools.values():
            info = tool.get_info()
            param_desc = ", ".join([
                f"{p['name']}({p['type']})"
                for p in info["parameters"]
            ])
            descriptions.append(
                f"- {info['name']}: {info['description']}\n"
                f"  Parameters: {param_desc if param_desc else 'none'}"
            )

        return "\n".join(descriptions)
