"""
OpenAI LLM提供商
支持GPT-4、GPT-3.5等模型
"""
from typing import List, Dict, Iterator
from openai import OpenAI

from .base import BaseLLMProvider, LLMConfig


class OpenAIProvider(BaseLLMProvider):
    """
    OpenAI LLM提供商

    支持GPT-4、GPT-3.5-turbo等模型
    """

    def __init__(self, config: LLMConfig):
        """
        初始化OpenAI提供商

        Args:
            config: LLM配置
                - api_key: OpenAI API密钥
                - base_url: API地址（可选，用于代理）
                - model: 模型名称（默认: gpt-3.5-turbo）
                - temperature: 温度参数
        """
        # 设置默认值
        if config.model == "default":
            config.model = "gpt-3.5-turbo"

        super().__init__(config)
        self._init_client()

    def _init_client(self):
        """初始化OpenAI客户端"""
        client_kwargs = {
            "api_key": self.config.api_key,
            "timeout": self.config.timeout,
        }

        # 如果提供了自定义base_url（如代理）
        if self.config.base_url:
            client_kwargs["base_url"] = self.config.base_url

        self._client = OpenAI(**client_kwargs)

    def chat(
        self,
        messages: List[Dict[str, str]],
        **kwargs
    ) -> str:
        """
        聊天接口

        Args:
            messages: 消息列表
            **kwargs: 额外参数

        Returns:
            str: 模型回复
        """
        self.validate_messages(messages)

        params = {
            "model": self.config.model,
            "messages": messages,
            "temperature": kwargs.get("temperature", self.config.temperature),
        }

        if "max_tokens" in kwargs:
            params["max_tokens"] = kwargs["max_tokens"]
        elif self.config.max_tokens:
            params["max_tokens"] = self.config.max_tokens

        try:
            response = self._client.chat.completions.create(**params)
            return response.choices[0].message.content.strip()

        except Exception as e:
            raise RuntimeError(f"OpenAI API error: {str(e)}")

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
            raise RuntimeError(f"OpenAI streaming error: {str(e)}")
