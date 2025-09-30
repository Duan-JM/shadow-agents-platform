"""
模型提供商工厂测试
"""

import pytest

from core.model_runtime.entities import ProviderType
from core.model_runtime.providers import (
    BaseEmbeddingProvider,
    BaseLLMProvider,
    ModelProviderFactory,
    OpenAIProvider,
    TEIProvider,
)


class TestModelProviderFactory:
    """模型提供商工厂测试类"""

    def test_get_llm_provider_openai(self):
        """测试获取 OpenAI LLM 提供商"""
        provider = ModelProviderFactory.get_llm_provider(ProviderType.OPENAI)
        assert isinstance(provider, BaseLLMProvider)
        assert isinstance(provider, OpenAIProvider)

    def test_get_llm_provider_unsupported(self):
        """测试获取不支持的 LLM 提供商"""
        with pytest.raises(ValueError, match="Unsupported LLM provider type"):
            ModelProviderFactory.get_llm_provider(ProviderType.TEI)

    def test_get_embedding_provider_tei(self):
        """测试获取 TEI 向量化提供商"""
        provider = ModelProviderFactory.get_embedding_provider(ProviderType.TEI)
        assert isinstance(provider, BaseEmbeddingProvider)
        assert isinstance(provider, TEIProvider)

    def test_get_embedding_provider_unsupported(self):
        """测试获取不支持的向量化提供商"""
        with pytest.raises(ValueError, match="Unsupported embedding provider type"):
            ModelProviderFactory.get_embedding_provider(ProviderType.OPENAI)

    def test_get_provider_openai(self):
        """测试自动获取 OpenAI 提供商"""
        provider = ModelProviderFactory.get_provider(ProviderType.OPENAI)
        assert isinstance(provider, OpenAIProvider)

    def test_get_provider_tei(self):
        """测试自动获取 TEI 提供商"""
        provider = ModelProviderFactory.get_provider(ProviderType.TEI)
        assert isinstance(provider, TEIProvider)

    def test_get_provider_singleton(self):
        """测试提供商单例模式"""
        provider1 = ModelProviderFactory.get_llm_provider(ProviderType.OPENAI)
        provider2 = ModelProviderFactory.get_llm_provider(ProviderType.OPENAI)
        assert provider1 is provider2
