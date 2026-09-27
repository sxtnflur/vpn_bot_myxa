import logging
from urllib.parse import quote

from application.errors import SessionError
from infra.xui_vpn.clients.get.schemas import GetClientObject, GetClientResponse
from infra.xui_vpn.shared.base import BaseXuiMethod


class GetClient(BaseXuiMethod):
    async def __call__(self, email: str) -> GetClientObject | None:
        """:return: None, если клиента с таким email нет"""
        # email может прийти от пользователя — экранируем, чтобы он не менял путь запроса
        url = self._base_url + f'/panel/api/clients/get/{quote(email, safe="")}'
        try:
            response = await self._session.get(url)
        except SessionError as e:
            if e.status == 404:
                return None
            raise
        result = GetClientResponse.model_validate(response, by_alias=True)
        if not result.success or result.obj is None:
            logging.info('3x-ui: клиент %r не найден: %s', email, result.msg)
            return None
        return result.obj
