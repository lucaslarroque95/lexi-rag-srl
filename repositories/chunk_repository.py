from abc import ABC, abstractmethod

from models.chunk import DocumentChunk


class ChunkRepository(ABC):
    @abstractmethod
    def save_many(self, chunks: list[DocumentChunk]) -> list[DocumentChunk]: ...
