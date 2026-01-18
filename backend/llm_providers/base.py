"""
LLM提供商抽象基类
定义统一的LLM接口
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Dict, Optional, Iterator


@dataclass
class LLMConfig:
    """LLM配置"""
    api_key: str
    base_url: Optional[str] = None
    model: str = "default"
    temperature: float = 0.4
    max_tokens: Optional[int] = None
    timeout: int = 60


class BaseLLMProvider(ABC):
    """
    LLM提供商抽象基类

    所有LLM提供商必须实现这个接口
    """

    def __init__(self, config: LLMConfig):
        self.config = config
        self._client = None

    @abstractmethod
    def _init_client(self):
        """初始化客户端（子类实现）"""
        pass

    @abstractmethod
    def chat(
        self,
        messages: List[Dict[str, str]],
        **kwargs
    ) -> str:
        """
        同步聊天接口

        Args:
            messages: 消息列表，格式 [{"role": "user", "content": "..."}]
            **kwargs: 额外参数（temperature, max_tokens等）

        Returns:
            str: 模型回复
        """
        pass

    @abstractmethod
    def stream_chat(
        self,
        messages: List[Dict[str, str]],
        **kwargs
    ) -> Iterator[str]:
        """
        流式聊天接口

        Args:
            messages: 消息列表
            **kwargs: 额外参数

        Yields:
            str: 模型回复的文本片段
        """
        pass

    def validate_messages(self, messages: List[Dict[str, str]]) -> bool:
        """验证消息格式"""
        if not messages:
            raise ValueError("Messages list is empty")

        for msg in messages:
            if not isinstance(msg, dict):
                raise ValueError(f"Message must be dict, got {type(msg)}")
            if "role" not in msg or "content" not in msg:
                raise ValueError(f"Message must have 'role' and 'content', got {msg}")
            if msg["role"] not in ["system", "user", "assistant"]:
                raise ValueError(f"Invalid role: {msg['role']}")

        return True

    def get_provider_name(self) -> str:
        """获取提供商名称"""
        return self.__class__.__name__.replace("Provider", "")

    def get_model_info(self) -> Dict[str, str]:
        """获取模型信息"""
        return {
            "provider": self.get_provider_name(),
            "model": self.config.model,
            "base_url": self.config.base_url or "default",
        }
