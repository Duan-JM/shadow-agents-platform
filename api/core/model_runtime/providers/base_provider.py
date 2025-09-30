"""
模型提供商基类
"""

from abc import ABC, abstractmethod
from typing import Generator, Optional

from core.model_runtime.entities.model_entities import (
    EmbeddingResult,
    LLMMessage,
    LLMResult,
    LLMResultChunk,
    ModelConfig,
    ProviderCredentials,
)


class BaseModelProvider(ABC):
    """模型提供商基类"""

    @abstractmethod
    def validate_credentials(self, credentials: ProviderCredentials) -> bool:
        """
        验证凭证是否有效

        Args:
            credentials: 提供商凭证

        Returns:
            bool: 凭证是否有效

        Raises:
            Exception: 验证失败时抛出异常
        """
        pass

    @abstractmethod
    def get_available_models(self, credentials: ProviderCredentials) -> list[str]:
        """
        获取可用的模型列表

        Args:
            credentials: 提供商凭证

        Returns:
            list[str]: 模型名称列表
        """
        pass


class BaseLLMProvider(BaseModelProvider):
    """LLM 提供商基类"""

    @abstractmethod
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
        """
        pass

    @abstractmethod
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
        """
        pass


class BaseEmbeddingProvider(BaseModelProvider):
    """向量化提供商基类"""

    @abstractmethod
    def embed_documents(
        self,
        credentials: ProviderCredentials,
        model: str,
        texts: list[str],
    ) -> EmbeddingResult:
        """
        对文档进行向量化

        Args:
            credentials: 提供商凭证
            model: 模型名称
            texts: 文本列表

        Returns:
            EmbeddingResult: 向量化结果
        """
        pass

    @abstractmethod
    def embed_query(
        self,
        credentials: ProviderCredentials,
        model: str,
        text: str,
    ) -> list[float]:
        """
        对查询文本进行向量化

        Args:
            credentials: 提供商凭证
            model: 模型名称
            text: 查询文本

        Returns:
            list[float]: 向量
        """
        pass
