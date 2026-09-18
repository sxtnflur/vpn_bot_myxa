import logging
from typing import Iterable, Any
import asyncio
import ssl
import certifi
from aiohttp import BasicAuth, ClientSession, TCPConnector
from aiohttp.hdrs import USER_AGENT
from aiohttp.http import SERVER_SOFTWARE
from infra.client.session.base import BaseSession


_ProxyBasic = str | tuple[str, BasicAuth]
_ProxyChain = Iterable[_ProxyBasic]
_ProxyType = _ProxyChain | _ProxyBasic


class AiohttpSession(BaseSession):
    def __init__(self, headers: dict | None = None, limit: int = 100, **kwargs: Any) -> None:
        """
        Client session based on aiohttp.

        :param proxy: The proxy to be used for requests. Default is None.
        :param limit: The total number of simultaneous connections. Default is 100.
        :param kwargs: Additional keyword arguments.
        """
        super().__init__(**kwargs)

        self._headers: dict | None = headers
        self._session: ClientSession | None = None

        self._connector_type: type[TCPConnector] = TCPConnector
        self._connector_init: dict[str, Any] = {
            "ssl": ssl.create_default_context(cafile=certifi.where()),
            "limit": limit,
            "ttl_dns_cache": 3600,  # Workaround for https://github.com/aiogram/aiogram/issues/1500
        }
        self._should_reset_connector = True  # flag determines connector state

    async def get(self, url: str, params: dict | None = None):
        session = await self.create_session()
        print(f'{session.headers=}')
        response = await session.get(url, params=params)
        response.raise_for_status()
        return await response.json()

    async def post(self, url: str, data: dict | None = None, params: dict | None = None):
        session = await self.create_session()
        response = await session.post(url, params=params, json=data)
        response.raise_for_status()
        return await response.json()

    async def create_session(self) -> ClientSession:
        if self._should_reset_connector:
            await self.close()

        if self._session is None or self._session.closed:
            self._session = ClientSession(
                connector=self._connector_type(**self._connector_init),
                headers={
                    USER_AGENT: SERVER_SOFTWARE,
                } | self._headers,
            )
            self._should_reset_connector = False

        return self._session

    async def close(self) -> None:
        if self._session is not None and not self._session.closed:
            await self._session.close()

            # Wait 250 ms for the underlying SSL connections to close
            # https://docs.aiohttp.org/en/stable/client_advanced.html#graceful-shutdown
            await asyncio.sleep(0.25)