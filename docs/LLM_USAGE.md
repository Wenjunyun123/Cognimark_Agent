# 多LLM提供商使用指南

## 概述

CogniMark 现在支持多种LLM提供商，包括：
- **DeepSeek** - 默认提供商，支持DeepSeek-V3和DeepSeek-V3.2
- **Minimax** - 支持Minimax-2.1
- **OpenAI** - 支持GPT-3.5和GPT-4

## 快速开始

### 1. 环境变量配置

在系统环境变量中设置API密钥：

```bash
# DeepSeek
export DEEPSEEK_API_KEY="your-deepseek-api-key"

# Minimax
export MINIMAX_API_KEY="your-minimax-api-key"

# OpenAI
export OPENAI_API_KEY="your-openai-api-key"
```

或在 `backend/config.py` 中直接配置。

### 2. 使用新版LLMService

```python
from llm_service import LLMService

# 创建DeepSeek服务
service = LLMService(provider="deepseek")

# 发送消息
messages = [
    {"role": "user", "content": "Hello!"}
]
response = service.chat(messages)
print(response)
```

### 3. 切换提供商

```python
# 创建DeepSeek服务
service = LLMService(provider="deepseek")

# 切换到Minimax
service.switch_provider("minimax")

# 切换到OpenAI
service.switch_provider("openai")

# 查看当前提供商
info = service.get_provider_info()
print(info)
# {'provider': 'OpenAI', 'model': 'gpt-3.5-turbo', 'base_url': 'default'}
```

## 向后兼容

旧的 `DeepSeekLLM` 类仍然可用：

```python
from llm_service import DeepSeekLLM

# 使用旧接口
llm = DeepSeekLLM()
response = llm.chat(
    system_prompt="You are a helpful assistant",
    user_prompt="Hello!"
)
```

## 提供商特定配置

### DeepSeek

```python
service = LLMService(
    provider="deepseek",
    model="deepseek-chat",  # 或 "deepseek-coder"
    temperature=0.4,
    api_key="your-api-key"  # 可选，默认从环境变量读取
)
```

### Minimax

```python
service = LLMService(
    provider="minimax",
    model="abab6.5s-chat",  # Minimax-2.1
    temperature=0.4,
    api_key="your-api-key"
)
```

### OpenAI

```python
service = LLMService(
    provider="openai",
    model="gpt-3.5-turbo",  # 或 "gpt-4"
    temperature=0.4,
    api_key="your-api-key"
)
```

## 流式响应

```python
service = LLMService(provider="deepseek")

messages = [{"role": "user", "content": "Tell me a story"}]

for chunk in service.stream_chat(messages):
    print(chunk, end="", flush=True)
```

## 在Agent中使用

### 更新现有Agent

现有Agent自动使用新的多LLM系统，无需修改代码：

```python
from agents import ProductSelectionAgent
from llm_service import DeepSeekLLM  # 仍然可用

llm = DeepSeekLLM()
agent = ProductSelectionAgent(default_store, llm)
```

### 使用新LLMService

```python
from agents import ProductSelectionAgent
from llm_service import LLMService

# 使用Minimax
llm_service = LLMService(provider="minimax")

# 注意：需要适配Agent接口，或使用包装器
```

## 错误处理

```python
from llm_service import LLMService

try:
    service = LLMService(provider="unknown")
except ValueError as e:
    print(f"Unknown provider: {e}")

try:
    response = service.chat(messages)
except RuntimeError as e:
    print(f"API error: {e}")
```

## 配置优先级

1. 环境变量（最高优先级）
2. `config.py` 文件
3. 代码中的默认值（最低优先级）

## 测试

运行测试验证安装：

```bash
cd backend
python test_llm_providers.py
```

## API端点扩展

未来可以添加以下API端点：

- `GET /llm/providers` - 获取可用提供商列表
- `GET /llm/current` - 获取当前提供商信息
- `POST /llm/switch` - 切换提供商
- `POST /llm/chat` - 统一聊天接口（支持选择提供商）

## 性能考虑

- DeepSeek: 成本最低，适合大部分场景
- Minimax: 平衡性能和成本
- OpenAI: 质量最高，但成本也最高

建议：
- 开发测试：使用DeepSeek
- 生产环境：根据实际需求选择
- 成本敏感：优先使用DeepSeek或Minimax
