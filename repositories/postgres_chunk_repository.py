
from sqlmodel import Session

from db.orm_models import BookChunkORM
from models.chunk import DocumentChunk
from repositories.chunk_repository import ChunkRepository


class PostgresChunkRepository(ChunkRepository):
    def __init__(self, session: Session):
        self.session = session

    def save_many(self, chunks: list[DocumentChunk]) -> list[DocumentChunk]:
        orm_chunks = [
            BookChunkORM(
                book=chunk.book,
                chapter=chunk.chapter,
                chapter_index=chunk.chapter_index,
                source=chunk.source,
                content=chunk.content,
                embedding=chunk.embedding,
            )
            for chunk in chunks
        ]

        self.session.add_all(orm_chunks)
        self.session.commit()

        for orm_chunk in orm_chunks:
            self.session.refresh(orm_chunk)

        return [self._to_domain(orm_chunk) for orm_chunk in orm_chunks]

    @staticmethod
    def _to_domain(orm_chunk: BookChunkORM) -> DocumentChunk:
        return DocumentChunk(**orm_chunk.model_dump())
