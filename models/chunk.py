from dataclasses import dataclass, field


@dataclass
class DocumentChunk:
    book: str
    chapter: str
    chapter_index: int
    source: str
    content: str
    embedding: list[float] = field(default_factory=list)
    id: int | None = None
