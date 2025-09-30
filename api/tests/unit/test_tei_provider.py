"""
TEI Provider 单元测试
"""

import pytest
from pytest_mock import MockerFixture

from core.model_runtime.entities import (
    EmbeddingResult,
    ProviderCredentials,
    ProviderType,
)
from core.model_runtime.providers import TEIProvider


class TestTEIProvider:
    """TEI Provider 测试类"""

    @pytest.fixture
    def provider(self):
        """创建 TEI Provider 实例"""
        return TEIProvider()

    @pytest.fixture
    def credentials(self):
        """创建测试凭证"""
        return ProviderCredentials(provider_type=ProviderType.TEI, credentials={"base_url": "http://localhost:8080"})

    def test_validate_credentials_success(self, provider, credentials, mocker: MockerFixture):
        """测试凭证验证成功"""
        # Mock httpx.Client.get
        mock_response = mocker.Mock()
        mock_response.raise_for_status = mocker.Mock()
        mock_client = mocker.Mock()
        mock_client.get.return_value = mock_response
        mock_client.__enter__ = mocker.Mock(return_value=mock_client)
        mock_client.__exit__ = mocker.Mock(return_value=False)
        mocker.patch("httpx.Client", return_value=mock_client)

        result = provider.validate_credentials(credentials)
        assert result is True

    def test_validate_credentials_missing_base_url(self, provider):
        """测试凭证验证缺少 base_url"""
        creds = ProviderCredentials(provider_type=ProviderType.TEI, credentials={})
        with pytest.raises(ValueError, match="base_url is required"):
            provider.validate_credentials(creds)

    def test_get_available_models(self, provider, credentials):
        """测试获取可用模型列表"""
        models = provider.get_available_models(credentials)
        assert len(models) == 1
        assert models[0] == "tei-embedding"

    def test_embed_documents_success(self, provider, credentials, mocker: MockerFixture):
        """测试文档向量化成功"""
        # Mock httpx.Client.post
        mock_response = mocker.Mock()
        mock_response.raise_for_status = mocker.Mock()
        mock_response.json.return_value = [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]]
        mock_client = mocker.Mock()
        mock_client.post.return_value = mock_response
        mock_client.__enter__ = mocker.Mock(return_value=mock_client)
        mock_client.__exit__ = mocker.Mock(return_value=False)
        mocker.patch("httpx.Client", return_value=mock_client)

        texts = ["Hello world", "Test document"]
        result = provider.embed_documents(credentials, "tei-embedding", texts)

        assert isinstance(result, EmbeddingResult)
        assert result.model == "tei-embedding"
        assert len(result.embeddings) == 2
        assert result.embeddings[0] == [0.1, 0.2, 0.3]
        assert result.embeddings[1] == [0.4, 0.5, 0.6]
        assert result.usage.prompt_tokens > 0

    def test_embed_documents_empty_texts(self, provider, credentials):
        """测试向量化空文本列表"""
        with pytest.raises(ValueError, match="texts cannot be empty"):
            provider.embed_documents(credentials, "tei-embedding", [])

    def test_embed_query_success(self, provider, credentials, mocker: MockerFixture):
        """测试查询向量化成功"""
        # Mock httpx.Client.post
        mock_response = mocker.Mock()
        mock_response.raise_for_status = mocker.Mock()
        mock_response.json.return_value = [[0.1, 0.2, 0.3]]
        mock_client = mocker.Mock()
        mock_client.post.return_value = mock_response
        mock_client.__enter__ = mocker.Mock(return_value=mock_client)
        mock_client.__exit__ = mocker.Mock(return_value=False)
        mocker.patch("httpx.Client", return_value=mock_client)

        text = "Hello world"
        embedding = provider.embed_query(credentials, "tei-embedding", text)

        assert isinstance(embedding, list)
        assert len(embedding) == 3
        assert embedding == [0.1, 0.2, 0.3]
