from abc import ABC, abstractmethod
from types import TracebackType

from typing_extensions import Self


class BaseSession(ABC):
    def __init__(self, headers: dict | None = None):
        self._headers = headers

    @abstractmethod
    async def get(self, url: str, params: dict | None = None): pass

    @abstractmethod
    async def post(self, url: str, data: dict | None = None, params: dict | None = None): pass

    @abstractmethod
    async def close(self) -> None:  # pragma: no cover
        """
        Close client session
        """

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        await self.close()
