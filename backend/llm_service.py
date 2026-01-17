from typing import Optional, List, Dict
from openai import OpenAI
import config

class DeepSeekLLM:
    """Action 模块：统一封装 DeepSeek 调用"""

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = config.DEEPSEEK_BASE_URL,
        model: str = config.DEEPSEEK_MODEL,
        temperature: float = 0.4,
    ):
        if api_key is None:
            api_key = config.DEEPSEEK_API_KEY
        
        # 简单的校验
        if not api_key or api_key.startswith("sk-xxxx"):
            print("Warning: Please provide a valid API Key in config.py or environment variables.")
        
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.model = model
        self.temperature = temperature

    def chat(self, system_prompt: str, user_prompt: str, history: Optional[List[Dict[str, str]]] = None) -> str:
        """
        发送聊天请求到 DeepSeek API
        支持多轮对话历史
        """
        try:
            messages = [{"role": "system", "content": system_prompt}]
            
            # 添加历史消息
            if history:
                messages.extend(history)
            
            # 添加当前用户消息
            messages.append({"role": "user", "content": user_prompt})
            
            resp = self.client.chat.completions.create(
                model=self.model,
                temperature=self.temperature,
                messages=messages,
            )
            return resp.choices[0].message.content.strip()
        except Exception as e:
            return f"Error calling LLM: {str(e)}"

