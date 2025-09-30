"""
模型提供商工厂
"""

from typing import Union

from core.model_runtime.entities.model_entities import ProviderType
from core.model_runtime.providers.base_provider import (
    BaseEmbeddingProvider,
    BaseLLMProvider,
)
from core.model_runtime.providers.openai_provider import OpenAIProvider
from core.model_runtime.providers.tei_provider import TEIProvider


class ModelProviderFactory:
    """模型提供商工厂"""

    _llm_providers: dict[ProviderType, BaseLLMProvider] = {}
    _embedding_providers: dict[ProviderType, BaseEmbeddingProvider] = {}

    @classmethod
    def get_llm_provider(cls, provider_type: ProviderType) -> BaseLLMProvider:
        """
        获取 LLM 提供商实例

        Args:
            provider_type: 提供商类型

        Returns:
            BaseLLMProvider: LLM 提供商实例

        Raises:
            ValueError: 不支持的提供商类型
        """
        if provider_type not in cls._llm_providers:
            if provider_type == ProviderType.OPENAI:
                cls._llm_providers[provider_type] = OpenAIProvider()
            else:
                raise ValueError(f"Unsupported LLM provider type: {provider_type}")

        return cls._llm_providers[provider_type]

    @classmethod
    def get_embedding_provider(cls, provider_type: ProviderType) -> BaseEmbeddingProvider:
        """
        获取向量化提供商实例

        Args:
            provider_type: 提供商类型

        Returns:
            BaseEmbeddingProvider: 向量化提供商实例

        Raises:
            ValueError: 不支持的提供商类型
        """
        if provider_type not in cls._embedding_providers:
            if provider_type == ProviderType.TEI:
                cls._embedding_providers[provider_type] = TEIProvider()
            else:
                raise ValueError(f"Unsupported embedding provider type: {provider_type}")

        return cls._embedding_providers[provider_type]

    @classmethod
    def get_provider(cls, provider_type: ProviderType) -> Union[BaseLLMProvider, BaseEmbeddingProvider]:
        """
        获取提供商实例（自动判断类型）

        Args:
            provider_type: 提供商类型

        Returns:
            Union[BaseLLMProvider, BaseEmbeddingProvider]: 提供商实例

        Raises:
            ValueError: 不支持的提供商类型
        """
        if provider_type == ProviderType.OPENAI:
            return cls.get_llm_provider(provider_type)
        elif provider_type == ProviderType.TEI:
            return cls.get_embedding_provider(provider_type)
        else:
            raise ValueError(f"Unsupported provider type: {provider_type}")
