
from pgvector.sqlalchemy import Vector
from sqlalchemy import Column
from sqlmodel import Field, SQLModel

from config import settings


class BookChunkORM(SQLModel, table=True):
    __tablename__ = "book_chunks"

    id: int | None = Field(default=None, primary_key=True)
    book: str
    chapter: str
    chapter_index: int
    source: str
    content: str
    embedding: list[float] = Field(
        sa_column=Column(Vector(settings.embedding_dimension))
    )
