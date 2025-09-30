"""
TEI (Text Embeddings Inference) 向量化提供商
"""

import httpx

from core.model_runtime.entities.model_entities import (
    EmbeddingResult,
    ModelUsage,
    ProviderCredentials,
)
from core.model_runtime.providers.base_provider import BaseEmbeddingProvider


class TEIProvider(BaseEmbeddingProvider):
    """TEI 向量化服务提供商"""

    def __init__(self):
        self.timeout = 30.0

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
        base_url = credentials.get("base_url")

        if not base_url:
            raise ValueError("base_url is required")

        # 尝试调用健康检查接口
        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.get(f"{base_url.rstrip('/')}/health")
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
            list[str]: 模型名称列表（TEI 通常只提供一个模型）
        """
        # TEI 服务通常只提供一个嵌入模型
        # 返回通用名称
        return ["tei-embedding"]

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

        Raises:
            ValueError: 参数错误
            httpx.HTTPError: 请求失败
        """
        base_url = credentials.get("base_url")

        if not base_url:
            raise ValueError("base_url is required")

        if not texts:
            raise ValueError("texts cannot be empty")

        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(
                    f"{base_url.rstrip('/')}/embed",
                    headers={"Content-Type": "application/json"},
                    json={"inputs": texts},
                )
                response.raise_for_status()
                embeddings = response.json()

                # TEI 返回的是向量列表
                # 计算 token 使用量（粗略估计：按字符数 / 4）
                total_chars = sum(len(text) for text in texts)
                estimated_tokens = total_chars // 4

                return EmbeddingResult(
                    model=model,
                    embeddings=embeddings,
                    usage=ModelUsage(
                        prompt_tokens=estimated_tokens,
                        completion_tokens=0,
                        total_tokens=estimated_tokens,
                    ),
                )
        except httpx.HTTPError as e:
            raise ValueError(f"Failed to embed documents: {str(e)}")

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

        Raises:
            ValueError: 参数错误
            httpx.HTTPError: 请求失败
        """
        result = self.embed_documents(credentials, model, [text])
        return result.embeddings[0]
