from abc import ABC, abstractmethod

from models.ingestion_message import IngestionMessage


class QueueConsumer(ABC):
    @abstractmethod
    def poll(self) -> IngestionMessage | None: ...

    @abstractmethod
    def ack(self, message: IngestionMessage) -> None: ...
