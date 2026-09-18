from abc import ABC, abstractmethod

from infra.client.session.base import BaseSession


class BaseXuiMethods(ABC):
    def __init__(self, base_url: str, api_key: str, session: BaseSession): pass


class BaseXuiMethod(ABC):
    def __init__(self, base_url: str, api_key: str, session: BaseSession):
        self._base_url = base_url
        self._api_key = api_key
        self._session = session

    @abstractmethod
    async def __call__(self, *args, **kwargs): pass
