
from langchain_text_splitters import RecursiveCharacterTextSplitter

from models.document_section import DocumentSection
from ports.text_splitter import TextSplitter


class LangchainTextSplitterAdapter(TextSplitter):
    def __init__(self, chunk_size: int, chunk_overlap: int):
        self._splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size, chunk_overlap=chunk_overlap
        )

    def split(self, sections: list[DocumentSection]) -> list[DocumentSection]:
        chunks: list[DocumentSection] = []

        for section in sections:
            for piece in self._splitter.split_text(section.content):
                chunks.append(
                    DocumentSection(
                        content=piece,
                        chapter=section.chapter,
                        chapter_index=section.chapter_index,
                        source=section.source,
                    )
                )

        return chunks
