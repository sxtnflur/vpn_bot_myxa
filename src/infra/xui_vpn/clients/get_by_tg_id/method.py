from infra.xui_vpn.clients.get.schemas import GetClientObject
from infra.xui_vpn.clients.get_by_tg_id.schemas import GetClientsByTgIdResponse
from infra.xui_vpn.shared.base import BaseXuiMethod


class GetClientsByTgId(BaseXuiMethod):
    async def __call__(self, tg_id: int) -> list[GetClientObject]:
        url = self._base_url + f'/panel/api/clients/get/tgId/{tg_id}'
        response = await self._session.get(url)
        result = GetClientsByTgIdResponse.model_validate(response, by_alias=True)
        return result.obj
