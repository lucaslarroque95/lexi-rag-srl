from abc import ABC, abstractmethod

from models.document_section import DocumentSection


class TextSplitter(ABC):
    @abstractmethod
    def split(self, sections: list[DocumentSection]) -> list[DocumentSection]: ...
