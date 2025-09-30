"""
OpenAI Provider 单元测试
"""

import json

import pytest
from pytest_mock import MockerFixture

from core.model_runtime.entities import (
    LLMMessage,
    LLMResult,
    LLMResultChunk,
    ModelConfig,
    ProviderCredentials,
    ProviderType,
)
from core.model_runtime.providers import OpenAIProvider


class TestOpenAIProvider:
    """OpenAI Provider 测试类"""

    @pytest.fixture
    def provider(self):
        """创建 OpenAI Provider 实例"""
        return OpenAIProvider()

    @pytest.fixture
    def credentials(self):
        """创建测试凭证"""
        return ProviderCredentials(
            provider_type=ProviderType.OPENAI,
            credentials={"api_key": "sk-test-key", "base_url": "https://api.openai.com/v1"},
        )

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

    def test_validate_credentials_missing_api_key(self, provider):
        """测试凭证验证缺少 API Key"""
        creds = ProviderCredentials(provider_type=ProviderType.OPENAI, credentials={})
        with pytest.raises(ValueError, match="api_key is required"):
            provider.validate_credentials(creds)

    def test_get_available_models(self, provider, credentials, mocker: MockerFixture):
        """测试获取可用模型列表"""
        # Mock httpx.Client.get
        mock_response = mocker.Mock()
        mock_response.raise_for_status = mocker.Mock()
        mock_response.json.return_value = {"data": [{"id": "gpt-3.5-turbo"}, {"id": "gpt-4"}, {"id": "gpt-4-turbo"}]}
        mock_client = mocker.Mock()
        mock_client.get.return_value = mock_response
        mock_client.__enter__ = mocker.Mock(return_value=mock_client)
        mock_client.__exit__ = mocker.Mock(return_value=False)
        mocker.patch("httpx.Client", return_value=mock_client)

        models = provider.get_available_models(credentials)
        assert len(models) == 3
        assert "gpt-3.5-turbo" in models
        assert "gpt-4" in models

    def test_invoke_success(self, provider, credentials, mocker: MockerFixture):
        """测试非流式调用成功"""
        # Mock httpx.Client.post
        mock_response = mocker.Mock()
        mock_response.raise_for_status = mocker.Mock()
        mock_response.json.return_value = {
            "model": "gpt-3.5-turbo",
            "choices": [{"message": {"content": "Hello! How can I help?"}, "finish_reason": "stop"}],
            "usage": {"prompt_tokens": 10, "completion_tokens": 8, "total_tokens": 18},
        }
        mock_client = mocker.Mock()
        mock_client.post.return_value = mock_response
        mock_client.__enter__ = mocker.Mock(return_value=mock_client)
        mock_client.__exit__ = mocker.Mock(return_value=False)
        mocker.patch("httpx.Client", return_value=mock_client)

        messages = [LLMMessage(role="user", content="Hello")]
        config = ModelConfig(model="gpt-3.5-turbo", temperature=0.7)

        result = provider.invoke(credentials, config, messages)

        assert isinstance(result, LLMResult)
        assert result.model == "gpt-3.5-turbo"
        assert result.content == "Hello! How can I help?"
        assert result.usage.prompt_tokens == 10
        assert result.usage.completion_tokens == 8
        assert result.usage.total_tokens == 18
        assert result.finish_reason == "stop"

    def test_invoke_empty_messages(self, provider, credentials):
        """测试调用时消息为空"""
        config = ModelConfig(model="gpt-3.5-turbo")
        with pytest.raises(ValueError, match="messages cannot be empty"):
            provider.invoke(credentials, config, [])

    def test_stream_invoke_success(self, provider, credentials, mocker: MockerFixture):
        """测试流式调用成功"""
        # Mock SSE 流数据
        sse_lines = [
            'data: {"model":"gpt-3.5-turbo","choices":[{"delta":{"content":"Hello"},"index":0}]}',
            'data: {"model":"gpt-3.5-turbo","choices":[{"delta":{"content":"!"},"index":0}]}',
            'data: {"model":"gpt-3.5-turbo","choices":[{"delta":{},"finish_reason":"stop","index":0}]}',
            "data: [DONE]",
        ]

        # Mock httpx.Client.stream
        mock_response = mocker.Mock()
        mock_response.raise_for_status = mocker.Mock()
        mock_response.iter_lines.return_value = iter(sse_lines)
        mock_response.__enter__ = mocker.Mock(return_value=mock_response)
        mock_response.__exit__ = mocker.Mock(return_value=False)

        mock_client = mocker.Mock()
        mock_client.stream.return_value = mock_response
        mock_client.__enter__ = mocker.Mock(return_value=mock_client)
        mock_client.__exit__ = mocker.Mock(return_value=False)
        mocker.patch("httpx.Client", return_value=mock_client)

        messages = [LLMMessage(role="user", content="Hello")]
        config = ModelConfig(model="gpt-3.5-turbo", temperature=0.7, stream=True)

        chunks = list(provider.stream_invoke(credentials, config, messages))

        assert len(chunks) == 2
        assert chunks[0].delta == "Hello"
        assert chunks[1].delta == "!"
        assert all(isinstance(chunk, LLMResultChunk) for chunk in chunks)

    def test_stream_invoke_empty_messages(self, provider, credentials):
        """测试流式调用时消息为空"""
        config = ModelConfig(model="gpt-3.5-turbo", stream=True)
        with pytest.raises(ValueError, match="messages cannot be empty"):
            list(provider.stream_invoke(credentials, config, []))
