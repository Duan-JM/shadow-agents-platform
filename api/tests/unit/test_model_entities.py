"""
模型运行时实体测试
"""

import pytest

from core.model_runtime.entities import (
    EmbeddingResult,
    LLMMessage,
    LLMResult,
    LLMResultChunk,
    ModelConfig,
    ModelType,
    ModelUsage,
    ProviderCredentials,
    ProviderType,
)


class TestModelEntities:
    """模型实体测试类"""

    def test_model_type_enum(self):
        """测试模型类型枚举"""
        assert ModelType.LLM == "llm"
        assert ModelType.TEXT_EMBEDDING == "text-embedding"

    def test_provider_type_enum(self):
        """测试提供商类型枚举"""
        assert ProviderType.OPENAI == "openai"
        assert ProviderType.TEI == "tei"

    def test_model_usage_creation(self):
        """测试模型使用量创建"""
        usage = ModelUsage(prompt_tokens=10, completion_tokens=20, total_tokens=30)
        assert usage.prompt_tokens == 10
        assert usage.completion_tokens == 20
        assert usage.total_tokens == 30

    def test_model_usage_addition(self):
        """测试模型使用量合并"""
        usage1 = ModelUsage(prompt_tokens=10, completion_tokens=20, total_tokens=30)
        usage2 = ModelUsage(prompt_tokens=5, completion_tokens=10, total_tokens=15)
        total = usage1 + usage2
        assert total.prompt_tokens == 15
        assert total.completion_tokens == 30
        assert total.total_tokens == 45

    def test_llm_message_creation(self):
        """测试 LLM 消息创建"""
        message = LLMMessage(role="user", content="Hello")
        assert message.role == "user"
        assert message.content == "Hello"

    def test_llm_result_creation(self):
        """测试 LLM 结果创建"""
        usage = ModelUsage(prompt_tokens=10, completion_tokens=20, total_tokens=30)
        result = LLMResult(
            model="gpt-3.5-turbo", content="Hello!", usage=usage, finish_reason="stop", system_fingerprint="fp_123"
        )
        assert result.model == "gpt-3.5-turbo"
        assert result.content == "Hello!"
        assert result.usage.total_tokens == 30
        assert result.finish_reason == "stop"
        assert result.system_fingerprint == "fp_123"

    def test_llm_result_chunk_creation(self):
        """测试 LLM 流式块创建"""
        chunk = LLMResultChunk(model="gpt-3.5-turbo", delta="Hello", finish_reason=None, index=0)
        assert chunk.model == "gpt-3.5-turbo"
        assert chunk.delta == "Hello"
        assert chunk.finish_reason is None
        assert chunk.index == 0

    def test_embedding_result_creation(self):
        """测试向量化结果创建"""
        usage = ModelUsage(prompt_tokens=10, total_tokens=10)
        embeddings = [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]]
        result = EmbeddingResult(model="text-embedding-ada-002", embeddings=embeddings, usage=usage)
        assert result.model == "text-embedding-ada-002"
        assert len(result.embeddings) == 2
        assert result.embeddings[0] == [0.1, 0.2, 0.3]
        assert result.usage.prompt_tokens == 10

    def test_provider_credentials_creation(self):
        """测试提供商凭证创建"""
        creds = ProviderCredentials(
            provider_type=ProviderType.OPENAI,
            credentials={"api_key": "sk-123", "base_url": "https://api.openai.com/v1"},
        )
        assert creds.provider_type == ProviderType.OPENAI
        assert creds.get("api_key") == "sk-123"
        assert creds.get("base_url") == "https://api.openai.com/v1"
        assert creds.get("missing_key", "default") == "default"

    def test_model_config_creation(self):
        """测试模型配置创建"""
        config = ModelConfig(
            model="gpt-3.5-turbo",
            temperature=0.7,
            max_tokens=100,
            top_p=1.0,
            frequency_penalty=0.0,
            presence_penalty=0.0,
            stop=["\n"],
            stream=False,
        )
        assert config.model == "gpt-3.5-turbo"
        assert config.temperature == 0.7
        assert config.max_tokens == 100
        assert config.stop == ["\n"]

    def test_model_config_to_dict(self):
        """测试模型配置转字典"""
        config = ModelConfig(model="gpt-3.5-turbo", temperature=0.8, max_tokens=200, stop=["\n", "END"])
        data = config.to_dict()
        assert data["model"] == "gpt-3.5-turbo"
        assert data["temperature"] == 0.8
        assert data["max_tokens"] == 200
        assert data["stop"] == ["\n", "END"]
        assert data["stream"] is False

    def test_model_config_to_dict_without_optional(self):
        """测试模型配置转字典（无可选字段）"""
        config = ModelConfig(model="gpt-3.5-turbo")
        data = config.to_dict()
        assert data["model"] == "gpt-3.5-turbo"
        assert data["temperature"] == 0.7
        assert "max_tokens" not in data
        assert "stop" not in data
