import os

# DeepSeek API Configuration
# 优先从环境变量获取，否则使用默认值（仅供 Demo 测试）
# 在生产环境中，请确保 API Key 不要硬编码在代码库中
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "sk-36a473800ac1418f89de6fefbaad999f")

DEEPSEEK_BASE_URL = "https://api.deepseek.com/v1"
DEEPSEEK_MODEL = "deepseek-chat"

