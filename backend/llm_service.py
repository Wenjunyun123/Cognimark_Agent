"""
LLM服务 - 统一的多LLM提供商支持

支持DeepSeek、Minimax、OpenAI等多种LLM提供商
保持向后兼容的DeepSeekLLM类
"""
from typing import Optional, List, Dict
import os

# 导入新的LLM提供商
from llm_providers import (
    BaseLLMProvider,
    LLMConfig,
    DeepSeekProvider,
    MinimaxProvider,
    OpenAIProvider,
)

# 导入旧版配置（向后兼容）
import config


class LLMService:
    """
    新版LLM服务 - 支持多提供商

    使用示例:
        service = LLMService(provider="deepseek")
        response = service.chat(messages)
    """

    # 提供商注册表
    PROVIDERS = {
        "deepseek": DeepSeekProvider,
        "minimax": MinimaxProvider,
        "openai": OpenAIProvider,
    }

    def __init__(
        self,
        provider: str = "deepseek",
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.4,
    ):
        """
        初始化LLM服务

        Args:
            provider: 提供商名称 ("deepseek", "minimax", "openai")
            api_key: API密钥（可选，默认从环境变量或config.py读取）
            model: 模型名称（可选）
            temperature: 温度参数
        """
        self.provider_name = provider
        self.provider = self._create_provider(provider, api_key, model, temperature)

    def _create_provider(
        self,
        provider_name: str,
        api_key: Optional[str],
        model: Optional[str],
        temperature: float,
    ) -> BaseLLMProvider:
        """创建LLM提供商实例"""
        provider_class = self.PROVIDERS.get(provider_name.lower())
        if not provider_class:
            raise ValueError(f"Unknown provider: {provider_name}. Available: {list(self.PROVIDERS.keys())}")

        # 获取API密钥
        if api_key is None:
            api_key = self._get_api_key(provider_name)

        # 获取模型名称
        if model is None:
            model = self._get_default_model(provider_name)

        # 获取base_url
        base_url = self._get_base_url(provider_name)

        # 创建配置
        llm_config = LLMConfig(
            api_key=api_key,
            base_url=base_url,
            model=model,
            temperature=temperature,
        )

        return provider_class(llm_config)

    def _get_api_key(self, provider: str) -> str:
        """从环境变量或config.py获取API密钥"""
        env_key = f"{provider.upper()}_API_KEY"
        api_key = os.getenv(env_key)

        if api_key:
            return api_key

        # 回退到config.py
        if provider == "deepseek" and hasattr(config, "DEEPSEEK_API_KEY"):
            return config.DEEPSEEK_API_KEY
        elif provider == "minimax" and hasattr(config, "MINIMAX_API_KEY"):
            return config.MINIMAX_API_KEY
        elif provider == "openai" and hasattr(config, "OPENAI_API_KEY"):
            return config.OPENAI_API_KEY

        raise ValueError(f"API key not found for {provider}. Set {env_key} environment variable.")

    def _get_default_model(self, provider: str) -> str:
        """获取默认模型名称"""
        if provider == "deepseek":
            return getattr(config, "DEEPSEEK_MODEL", "deepseek-chat")
        elif provider == "minimax":
            return getattr(config, "MINIMAX_MODEL", "abab6.5s-chat")
        elif provider == "openai":
            return getattr(config, "OPENAI_MODEL", "gpt-3.5-turbo")
        return "default"

    def _get_base_url(self, provider: str) -> Optional[str]:
        """获取API base URL"""
        if provider == "deepseek" and hasattr(config, "DEEPSEEK_BASE_URL"):
            return config.DEEPSEEK_BASE_URL
        elif provider == "minimax" and hasattr(config, "MINIMAX_BASE_URL"):
            return config.MINIMAX_BASE_URL
        return None

    def chat(
        self,
        messages: List[Dict[str, str]],
        **kwargs
    ) -> str:
        """
        发送聊天请求

        Args:
            messages: 消息列表 [{"role": "user", "content": "..."}]
            **kwargs: 额外参数

        Returns:
            str: 模型回复
        """
        return self.provider.chat(messages, **kwargs)

    def stream_chat(
        self,
        messages: List[Dict[str, str]],
        **kwargs
    ):
        """
        流式聊天

        Args:
            messages: 消息列表
            **kwargs: 额外参数

        Yields:
            str: 文本片段
        """
        return self.provider.stream_chat(messages, **kwargs)

    def switch_provider(self, provider: str, **kwargs):
        """切换LLM提供商"""
        self.provider_name = provider
        self.provider = self._create_provider(
            provider,
            kwargs.get("api_key"),
            kwargs.get("model"),
            kwargs.get("temperature", 0.4),
        )

    def get_provider_info(self) -> Dict[str, str]:
        """获取当前提供商信息"""
        return self.provider.get_model_info()


# ==================== 向后兼容层 ====================

class DeepSeekLLM:
    """
    向后兼容的DeepSeek LLM类

    保留原有API接口，内部使用新的LLMService
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = None,
        model: str = None,
        temperature: float = 0.4,
    ):
        """
        初始化DeepSeek LLM（向后兼容）

        Args:
            api_key: API密钥
            base_url: API地址
            model: 模型名称
            temperature: 温度参数
        """
        # 使用默认值
        if base_url is None:
            base_url = getattr(config, "DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1")
        if model is None:
            model = getattr(config, "DEEPSEEK_MODEL", "deepseek-chat")

        # 创建新的LLMService实例
        self._service = LLMService(
            provider="deepseek",
            api_key=api_key,
            model=model,
            temperature=temperature,
        )

        # 保存旧属性以保持兼容
        self.model = model
        self.temperature = temperature

        # 警告
        if api_key is None:
            default_key = getattr(config, "DEEPSEEK_API_KEY", "")
            if not default_key or default_key.startswith("sk-xxxx"):
                print("Warning: Please provide a valid API Key in config.py or environment variables.")

    def chat(
        self,
        system_prompt: str,
        user_prompt: str,
        history: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """
        发送聊天请求（向后兼容接口）

        Args:
            system_prompt: 系统提示词
            user_prompt: 用户提示词
            history: 对话历史

        Returns:
            str: 模型回复
        """
        try:
            # 构建消息列表
            messages = [{"role": "system", "content": system_prompt}]

            if history:
                messages.extend(history)

            messages.append({"role": "user", "content": user_prompt})

            # 使用新的LLMService
            return self._service.chat(messages)

        except Exception as e:
            return f"Error calling LLM: {str(e)}"

    def stream_chat(
        self,
        system_prompt: str,
        user_prompt: str,
        history: Optional[List[Dict[str, str]]] = None
    ):
        """
        流式聊天（向后兼容接口）

        Args:
            system_prompt: 系统提示词
            user_prompt: 用户提示词
            history: 对话历史

        Yields:
            str: 文本片段
        """
        try:
            # 构建消息列表
            messages = [{"role": "system", "content": system_prompt}]

            if history:
                messages.extend(history)

            messages.append({"role": "user", "content": user_prompt})

            # 使用新的LLMService的流式方法
            yield from self._service.stream_chat(messages)

        except Exception as e:
            yield f"Error calling LLM: {str(e)}"


# 导出
__all__ = [
    "LLMService",
    "DeepSeekLLM",  # 向后兼容
    "BaseLLMProvider",
    "LLMConfig",
]
