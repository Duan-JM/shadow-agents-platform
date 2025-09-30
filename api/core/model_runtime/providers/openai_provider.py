"""
OpenAI 模型提供商
"""

import json
from typing import Generator

import httpx

from core.model_runtime.entities.model_entities import (
    LLMMessage,
    LLMResult,
    LLMResultChunk,
    ModelConfig,
    ModelUsage,
    ProviderCredentials,
)
from core.model_runtime.providers.base_provider import BaseLLMProvider


class OpenAIProvider(BaseLLMProvider):
    """OpenAI 格式的 LLM 提供商"""

    def __init__(self):
        self.timeout = 60.0

    def validate_credentials(self, credentials: ProviderCredentials) -> bool:
        """
        验证凭证是否有效

        Args:
            credentials: 提供商凭证

        Returns:
            bool: 凭证是否有效

        Raises:
            ValueError: 凭证缺少必需字段
            httpx.HTTPError: 请求失败
        """
        api_key = credentials.get("api_key")
        base_url = credentials.get("base_url", "https://api.openai.com/v1")

        if not api_key:
            raise ValueError("api_key is required")

        # 尝试调用 models 接口验证
        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.get(
                    f"{base_url.rstrip('/')}/models",
                    headers={
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json",
                    },
                )
                response.raise_for_status()
                return True
        except httpx.HTTPError as e:
            raise ValueError(f"Failed to validate credentials: {str(e)}")

    def get_available_models(self, credentials: ProviderCredentials) -> list[str]:
        """
        获取可用的模型列表

        Args:
            credentials: 提供商凭证

        Returns:
            list[str]: 模型名称列表
        """
        api_key = credentials.get("api_key")
        base_url = credentials.get("base_url", "https://api.openai.com/v1")

        if not api_key:
            raise ValueError("api_key is required")

        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.get(
                    f"{base_url.rstrip('/')}/models",
                    headers={
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json",
                    },
                )
                response.raise_for_status()
                data = response.json()
                return [model["id"] for model in data.get("data", [])]
        except httpx.HTTPError as e:
            raise ValueError(f"Failed to get available models: {str(e)}")

    def invoke(
        self,
        credentials: ProviderCredentials,
        model_config: ModelConfig,
        messages: list[LLMMessage],
    ) -> LLMResult:
        """
        调用 LLM 模型（非流式）

        Args:
            credentials: 提供商凭证
            model_config: 模型配置
            messages: 消息列表

        Returns:
            LLMResult: LLM 调用结果

        Raises:
            ValueError: 参数错误
            httpx.HTTPError: 请求失败
        """
        api_key = credentials.get("api_key")
        base_url = credentials.get("base_url", "https://api.openai.com/v1")

        if not api_key:
            raise ValueError("api_key is required")

        if not messages:
            raise ValueError("messages cannot be empty")

        # 构建请求体
        request_data = model_config.to_dict()
        request_data["messages"] = [{"role": msg.role, "content": msg.content} for msg in messages]
        request_data["stream"] = False

        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(
                    f"{base_url.rstrip('/')}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json",
                    },
                    json=request_data,
                )
                response.raise_for_status()
                data = response.json()

                # 解析响应
                choice = data["choices"][0]
                usage_data = data.get("usage", {})

                return LLMResult(
                    model=data["model"],
                    content=choice["message"]["content"],
                    usage=ModelUsage(
                        prompt_tokens=usage_data.get("prompt_tokens", 0),
                        completion_tokens=usage_data.get("completion_tokens", 0),
                        total_tokens=usage_data.get("total_tokens", 0),
                    ),
                    finish_reason=choice.get("finish_reason"),
                    system_fingerprint=data.get("system_fingerprint"),
                )
        except httpx.HTTPError as e:
            raise ValueError(f"Failed to invoke model: {str(e)}")

    def stream_invoke(
        self,
        credentials: ProviderCredentials,
        model_config: ModelConfig,
        messages: list[LLMMessage],
    ) -> Generator[LLMResultChunk, None, None]:
        """
        调用 LLM 模型（流式）

        Args:
            credentials: 提供商凭证
            model_config: 模型配置
            messages: 消息列表

        Yields:
            LLMResultChunk: LLM 流式输出块

        Raises:
            ValueError: 参数错误
            httpx.HTTPError: 请求失败
        """
        api_key = credentials.get("api_key")
        base_url = credentials.get("base_url", "https://api.openai.com/v1")

        if not api_key:
            raise ValueError("api_key is required")

        if not messages:
            raise ValueError("messages cannot be empty")

        # 构建请求体
        request_data = model_config.to_dict()
        request_data["messages"] = [{"role": msg.role, "content": msg.content} for msg in messages]
        request_data["stream"] = True

        try:
            with httpx.Client(timeout=self.timeout) as client:
                with client.stream(
                    "POST",
                    f"{base_url.rstrip('/')}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json",
                    },
                    json=request_data,
                ) as response:
                    response.raise_for_status()

                    # 解析 SSE 流
                    for line in response.iter_lines():
                        if not line:
                            continue

                        # 移除 "data: " 前缀
                        if line.startswith("data: "):
                            line = line[6:]

                        # 流结束标记
                        if line == "[DONE]":
                            break

                        try:
                            data = json.loads(line)
                            choice = data["choices"][0]

                            # 提取增量内容
                            delta = choice.get("delta", {})
                            content = delta.get("content", "")

                            if content:
                                yield LLMResultChunk(
                                    model=data["model"],
                                    delta=content,
                                    finish_reason=choice.get("finish_reason"),
                                    index=choice.get("index", 0),
                                )
                        except json.JSONDecodeError:
                            # 忽略无法解析的行
                            continue
        except httpx.HTTPError as e:
            raise ValueError(f"Failed to stream invoke model: {str(e)}")
