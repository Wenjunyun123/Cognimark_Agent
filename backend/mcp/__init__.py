"""
MCP (Model Context Protocol) 工具调用框架

提供可插拔的工具系统，支持Agent调用外部工具
"""
from .base_tool import BaseTool, ToolResult, ToolError
from .tool_manager import ToolManager

__all__ = [
    "BaseTool",
    "ToolResult",
    "ToolError",
    "ToolManager",
]
