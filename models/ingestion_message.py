from dataclasses import dataclass


@dataclass
class IngestionMessage:
    book: str
    file_path: str
