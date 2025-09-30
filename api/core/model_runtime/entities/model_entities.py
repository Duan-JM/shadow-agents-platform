"""
模型运行时实体类
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional


class ModelType(str, Enum):
    """模型类型枚举"""

    LLM = "llm"  # 大语言模型
    TEXT_EMBEDDING = "text-embedding"  # 文本向量化


class ProviderType(str, Enum):
    """提供商类型枚举"""

    OPENAI = "openai"
    TEI = "tei"  # Text Embeddings Inference


@dataclass
class ModelUsage:
    """模型使用量统计"""

    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0

    def __add__(self, other: "ModelUsage") -> "ModelUsage":
        """合并使用量统计"""
        return ModelUsage(
            prompt_tokens=self.prompt_tokens + other.prompt_tokens,
            completion_tokens=self.completion_tokens + other.completion_tokens,
            total_tokens=self.total_tokens + other.total_tokens,
        )


@dataclass
class LLMMessage:
    """LLM 消息"""

    role: str  # system, user, assistant
    content: str


@dataclass
class LLMResult:
    """LLM 调用结果"""

    model: str
    content: str
    usage: ModelUsage
    finish_reason: Optional[str] = None
    system_fingerprint: Optional[str] = None


@dataclass
class LLMResultChunk:
    """LLM 流式输出块"""

    model: str
    delta: str  # 增量内容
    finish_reason: Optional[str] = None
    index: int = 0


@dataclass
class EmbeddingResult:
    """文本向量化结果"""

    model: str
    embeddings: list[list[float]]  # 向量列表
    usage: ModelUsage


@dataclass
class ProviderCredentials:
    """提供商凭证"""

    provider_type: ProviderType
    credentials: dict[str, Any]  # 凭证信息 (api_key, base_url, etc.)

    def get(self, key: str, default: Any = None) -> Any:
        """获取凭证值"""
        return self.credentials.get(key, default)


@dataclass
class ModelConfig:
    """模型配置"""

    model: str
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    top_p: float = 1.0
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    stop: Optional[list[str]] = None
    stream: bool = False

    def to_dict(self) -> dict[str, Any]:
        """转换为字典"""
        data = {
            "model": self.model,
            "temperature": self.temperature,
            "top_p": self.top_p,
            "frequency_penalty": self.frequency_penalty,
            "presence_penalty": self.presence_penalty,
            "stream": self.stream,
        }
        if self.max_tokens is not None:
            data["max_tokens"] = self.max_tokens
        if self.stop is not None:
            data["stop"] = self.stop
        return data
