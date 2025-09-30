# 模型提供商使用指南

## 概述

Shadow Agents Platform 的模型运行时模块提供了统一的接口来调用不同的 LLM 和向量化服务。目前支持：

- **OpenAI Provider**: 支持 OpenAI 格式的 Chat Completion API（流式和非流式）
- **TEI Provider**: 支持 Text Embeddings Inference (TEI) 向量化服务

## 快速开始

### 1. OpenAI Provider 使用示例

#### 非流式调用

```python
from core.model_runtime import (
    ModelProviderFactory,
    ProviderType,
    ProviderCredentials,
    ModelConfig,
    LLMMessage,
)

# 创建凭证
credentials = ProviderCredentials(
    provider_type=ProviderType.OPENAI,
    credentials={
        "api_key": "sk-your-api-key",
        "base_url": "https://api.openai.com/v1",  # 可选，默认为 OpenAI 官方地址
    }
)

# 获取提供商实例
provider = ModelProviderFactory.get_llm_provider(ProviderType.OPENAI)

# 配置模型参数
config = ModelConfig(
    model="gpt-3.5-turbo",
    temperature=0.7,
    max_tokens=1000,
)

# 准备消息
messages = [
    LLMMessage(role="system", content="You are a helpful assistant."),
    LLMMessage(role="user", content="Hello, how are you?"),
]

# 调用模型
result = provider.invoke(credentials, config, messages)

print(f"回答: {result.content}")
print(f"使用量: {result.usage.total_tokens} tokens")
```

#### 流式调用

```python
# 配置为流式模式
config = ModelConfig(
    model="gpt-3.5-turbo",
    temperature=0.7,
    stream=True,  # 启用流式输出
)

# 流式调用
for chunk in provider.stream_invoke(credentials, config, messages):
    print(chunk.delta, end="", flush=True)
```

### 2. TEI Provider 使用示例

#### 文档向量化

```python
from core.model_runtime import (
    ModelProviderFactory,
    ProviderType,
    ProviderCredentials,
)

# 创建凭证
credentials = ProviderCredentials(
    provider_type=ProviderType.TEI,
    credentials={
        "base_url": "http://localhost:8080",  # TEI 服务地址
    }
)

# 获取提供商实例
provider = ModelProviderFactory.get_embedding_provider(ProviderType.TEI)

# 对多个文档进行向量化
texts = [
    "这是第一个文档",
    "这是第二个文档",
    "这是第三个文档",
]

result = provider.embed_documents(
    credentials=credentials,
    model="tei-embedding",  # TEI 通常只提供一个模型
    texts=texts,
)

print(f"向量维度: {len(result.embeddings[0])}")
print(f"文档数量: {len(result.embeddings)}")
print(f"使用量: {result.usage.total_tokens} tokens")
```

#### 查询向量化

```python
# 对单个查询文本进行向量化
query = "搜索相关文档"
embedding = provider.embed_query(
    credentials=credentials,
    model="tei-embedding",
    text=query,
)

print(f"查询向量维度: {len(embedding)}")
```

## 凭证验证

所有提供商都支持凭证验证：

```python
try:
    is_valid = provider.validate_credentials(credentials)
    print(f"凭证验证结果: {is_valid}")
except ValueError as e:
    print(f"凭证验证失败: {e}")
```

## 获取可用模型

```python
# OpenAI Provider
openai_provider = ModelProviderFactory.get_llm_provider(ProviderType.OPENAI)
models = openai_provider.get_available_models(credentials)
print(f"可用模型: {models}")

# TEI Provider
tei_provider = ModelProviderFactory.get_embedding_provider(ProviderType.TEI)
models = tei_provider.get_available_models(credentials)
print(f"可用模型: {models}")
```

## 配置说明

### OpenAI Provider 配置

| 参数 | 类型 | 必需 | 默认值 | 说明 |
|------|------|------|--------|------|
| api_key | str | 是 | - | OpenAI API Key |
| base_url | str | 否 | https://api.openai.com/v1 | API 基础地址 |

### TEI Provider 配置

| 参数 | 类型 | 必需 | 默认值 | 说明 |
|------|------|------|--------|------|
| base_url | str | 是 | - | TEI 服务地址 |

### ModelConfig 参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| model | str | - | 模型名称 |
| temperature | float | 0.7 | 温度参数 (0-2) |
| max_tokens | int | None | 最大生成 token 数 |
| top_p | float | 1.0 | 核采样参数 |
| frequency_penalty | float | 0.0 | 频率惩罚 (-2 到 2) |
| presence_penalty | float | 0.0 | 存在惩罚 (-2 到 2) |
| stop | list[str] | None | 停止序列 |
| stream | bool | False | 是否启用流式输出 |

## 错误处理

```python
from core.model_runtime import ModelProviderFactory, ProviderType

provider = ModelProviderFactory.get_llm_provider(ProviderType.OPENAI)

try:
    result = provider.invoke(credentials, config, messages)
except ValueError as e:
    # 参数错误或 API 调用失败
    print(f"调用失败: {e}")
except Exception as e:
    # 其他错误
    print(f"未知错误: {e}")
```

## 使用建议

1. **凭证管理**: 不要在代码中硬编码 API Key，使用环境变量或配置文件
2. **错误重试**: 网络请求可能失败，建议实现重试机制
3. **流式输出**: 对于长文本生成，建议使用流式输出提升用户体验
4. **Token 管理**: 监控 token 使用量，避免超出配额
5. **Base URL**: OpenAI Provider 支持自定义 base_url，可用于代理或兼容服务

## 扩展新的提供商

要添加新的模型提供商，需要：

1. 继承 `BaseLLMProvider` 或 `BaseEmbeddingProvider`
2. 实现所有抽象方法
3. 在 `ModelProviderFactory` 中注册新的提供商类型

示例：

```python
from core.model_runtime.providers import BaseLLMProvider

class MyCustomProvider(BaseLLMProvider):
    def validate_credentials(self, credentials):
        # 实现凭证验证逻辑
        pass
    
    def get_available_models(self, credentials):
        # 实现获取模型列表逻辑
        pass
    
    def invoke(self, credentials, model_config, messages):
        # 实现非流式调用逻辑
        pass
    
    def stream_invoke(self, credentials, model_config, messages):
        # 实现流式调用逻辑
        pass
```

## 测试

所有提供商都有完整的单元测试覆盖：

```bash
# 运行所有模型提供商测试
pytest tests/unit/test_model_entities.py
pytest tests/unit/test_openai_provider.py
pytest tests/unit/test_tei_provider.py
pytest tests/unit/test_provider_factory.py
```

## 参考资料

- [OpenAI API 文档](https://platform.openai.com/docs/api-reference)
- [TEI 文档](https://github.com/huggingface/text-embeddings-inference)
