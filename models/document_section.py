from dataclasses import dataclass


@dataclass
class DocumentSection:
    content: str
    chapter: str
    chapter_index: int
    source: str
