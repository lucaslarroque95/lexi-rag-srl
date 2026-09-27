from abc import ABC, abstractmethod

from models.document_section import DocumentSection


class DocumentLoader(ABC):
    @abstractmethod
    def load(self, file_path: str) -> list[DocumentSection]: ...
