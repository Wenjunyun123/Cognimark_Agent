"""
DeepSeek LLM提供商
支持DeepSeek-V3和DeepSeek-V3.2
"""
from typing import List, Dict, Iterator
from openai import OpenAI

from .base import BaseLLMProvider, LLMConfig


class DeepSeekProvider(BaseLLMProvider):
    """
    DeepSeek LLM提供商

    使用DeepSeek API（兼容OpenAI SDK）
    """

    def __init__(self, config: LLMConfig):
        """
        初始化DeepSeek提供商

        Args:
            config: LLM配置
                - api_key: DeepSeek API密钥
                - base_url: API地址（默认: https://api.deepseek.com/v1）
                - model: 模型名称（默认: deepseek-chat）
                - temperature: 温度参数
        """
        # 设置默认值
        if config.base_url is None:
            config.base_url = "https://api.deepseek.com/v1"
        if config.model == "default":
            config.model = "deepseek-chat"

        super().__init__(config)
        self._init_client()

    def _init_client(self):
        """初始化OpenAI客户端（DeepSeek兼容）"""
        self._client = OpenAI(
            api_key=self.config.api_key,
            base_url=self.config.base_url,
            timeout=self.config.timeout,
        )

    def chat(
        self,
        messages: List[Dict[str, str]],
        **kwargs
    ) -> str:
        """
        聊天接口

        Args:
            messages: 消息列表
            **kwargs: 额外参数（temperature, max_tokens等）

        Returns:
            str: 模型回复
        """
        # 验证消息格式
        self.validate_messages(messages)

        # 合并参数
        params = {
            "model": self.config.model,
            "messages": messages,
            "temperature": kwargs.get("temperature", self.config.temperature),
        }

        # 添加可选参数
        if "max_tokens" in kwargs:
            params["max_tokens"] = kwargs["max_tokens"]
        elif self.config.max_tokens:
            params["max_tokens"] = self.config.max_tokens

        try:
            response = self._client.chat.completions.create(**params)
            return response.choices[0].message.content.strip()

        except Exception as e:
            raise RuntimeError(f"DeepSeek API error: {str(e)}")

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
        self.validate_messages(messages)

        params = {
            "model": self.config.model,
            "messages": messages,
            "temperature": kwargs.get("temperature", self.config.temperature),
            "stream": True,
        }

        try:
            stream = self._client.chat.completions.create(**params)
            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    yield chunk.choices[0].delta.content

        except Exception as e:
            raise RuntimeError(f"DeepSeek streaming error: {str(e)}")
