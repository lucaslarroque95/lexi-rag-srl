
from models.chunk import DocumentChunk
from models.ingestion_message import IngestionMessage
from ports.document_loader import DocumentLoader
from ports.embedding_provider import EmbeddingProvider
from ports.text_splitter import TextSplitter
from repositories.chunk_repository import ChunkRepository


class IngestDocumentUseCase:
    def __init__(
        self,
        loader: DocumentLoader,
        splitter: TextSplitter,
        embedder: EmbeddingProvider,
        repository: ChunkRepository,
    ):
        self.loader = loader
        self.splitter = splitter
        self.embedder = embedder
        self.repository = repository

    def execute(self, message: IngestionMessage) -> list[DocumentChunk]:
        sections = self.loader.load(message.file_path)
        split_sections = self.splitter.split(sections)

        chunks = [
            DocumentChunk(
                book=message.book,
                chapter=section.chapter,
                chapter_index=section.chapter_index,
                source=section.source,
                content=section.content,
                embedding=self.embedder.embed(section.content),
            )
            for section in split_sections
        ]

        return self.repository.save_many(chunks)
