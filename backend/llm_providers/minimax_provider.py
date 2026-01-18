"""
Minimax LLM提供商
支持Minimax-2.1
"""
from typing import List, Dict, Iterator
import requests

from .base import BaseLLMProvider, LLMConfig


class MinimaxProvider(BaseLLMProvider):
    """
    Minimax LLM提供商

    使用Minimax API
    """

    def __init__(self, config: LLMConfig):
        """
        初始化Minimax提供商

        Args:
            config: LLM配置
                - api_key: Minimax API密钥
                - base_url: API地址
                - model: 模型名称（默认: abab6.5s-chat）
                - temperature: 温度参数
        """
        # 设置默认值
        if config.base_url is None:
            config.base_url = "https://api.minimax.chat/v1"
        if config.model == "default":
            config.model = "abab6.5s-chat"

        super().__init__(config)
        self._init_client()

    def _init_client(self):
        """初始化HTTP客户端"""
        self._session = requests.Session()
        self._session.headers.update({
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json",
        })

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

        # 构建请求
        url = f"{self.config.base_url}/chat/completions"
        payload = {
            "model": self.config.model,
            "messages": messages,
            "temperature": kwargs.get("temperature", self.config.temperature),
        }

        # 添加可选参数
        if "max_tokens" in kwargs:
            payload["max_tokens"] = kwargs["max_tokens"]
        elif self.config.max_tokens:
            payload["max_tokens"] = self.config.max_tokens

        try:
            response = self._session.post(
                url,
                json=payload,
                timeout=self.config.timeout,
            )
            response.raise_for_status()

            data = response.json()
            return data["choices"][0]["message"]["content"].strip()

        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Minimax API error: {str(e)}")

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

        url = f"{self.config.base_url}/chat/completions"
        payload = {
            "model": self.config.model,
            "messages": messages,
            "temperature": kwargs.get("temperature", self.config.temperature),
            "stream": True,
        }

        try:
            response = self._session.post(
                url,
                json=payload,
                timeout=self.config.timeout,
                stream=True,
            )
            response.raise_for_status()

            for line in response.iter_lines():
                if line:
                    line = line.decode("utf-8")
                    if line.startswith("data: "):
                        data_str = line[6:]  # Remove "data: " prefix
                        if data_str == "[DONE]":
                            break
                        # 解析SSE数据
                        # 这里需要根据实际Minimax API响应格式调整
                        # 简化示例：
                        if "choices" in data_str:
                            import json
                            data = json.loads(data_str)
                            if data["choices"]:
                                content = data["choices"][0].get("delta", {}).get("content")
                                if content:
                                    yield content

        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Minimax streaming error: {str(e)}")
