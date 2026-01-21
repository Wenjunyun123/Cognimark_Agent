"""
LLM配置文件

支持多种LLM提供商的配置
优先从环境变量读取，回退到默认值
"""
import os

# ==================== DeepSeek 配置 ====================
DEEPSEEK_API_KEY = os.getenv(
    "DEEPSEEK_API_KEY",
    "请替换为实际API Key"  # 请替换为实际API Key
)
DEEPSEEK_BASE_URL = os.getenv(
    "DEEPSEEK_BASE_URL",
    "https://api.deepseek.com/v1"
)
DEEPSEEK_MODEL = os.getenv(
    "DEEPSEEK_MODEL",
    "deepseek-chat"  # 或 "deepseek-coder"
)

# ==================== Minimax 配置 ====================
MINIMAX_API_KEY = os.getenv(
    "MINIMAX_API_KEY",
    ""  # 请设置环境变量
)
MINIMAX_BASE_URL = os.getenv(
    "MINIMAX_BASE_URL",
    "https://api.minimax.chat/v1"
)
MINIMAX_MODEL = os.getenv(
    "MINIMAX_MODEL",
    "abab6.5s-chat"  # Minimax-2.1
)

# ==================== OpenAI 配置 ====================
OPENAI_API_KEY = os.getenv(
    "OPENAI_API_KEY",
    ""  # 请设置环境变量
)
OPENAI_BASE_URL = os.getenv(
    "OPENAI_BASE_URL",
    ""  # 可选，用于代理
)
OPENAI_MODEL = os.getenv(
    "OPENAI_MODEL",
    "gpt-3.5-turbo"  # 或 "gpt-4"
)

# ==================== 默认LLM配置 ====================
DEFAULT_LLM_PROVIDER = os.getenv(
    "DEFAULT_LLM_PROVIDER",
    "deepseek"  # 可选: "deepseek", "minimax", "openai"
)

# ==================== 数据库配置 ====================
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./cognimark.db"
)

# ==================== 应用配置 ====================
APP_NAME = "CogniMark"
APP_VERSION = "2.0.0"
DEBUG = os.getenv("DEBUG", "False").lower() == "true"
