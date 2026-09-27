
from langchain_openai import OpenAIEmbeddings

from ports.embedding_provider import EmbeddingProvider


class OpenAIEmbeddingProvider(EmbeddingProvider):
    def __init__(self, model: str, api_key: str, dimension: int):
        self._client = OpenAIEmbeddings(model=model, api_key=api_key)
        self._dimension = dimension

    def embed(self, text: str) -> list[float]:
        return self._client.embed_query(text)

    @property
    def dimension(self) -> int:
        return self._dimension
