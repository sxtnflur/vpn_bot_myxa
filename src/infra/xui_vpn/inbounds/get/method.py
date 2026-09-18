from infra.xui_vpn.inbounds.get.schemas import InboundResponse
from infra.xui_vpn.inbounds.list.schemas import Inbound
from infra.xui_vpn.shared.base import BaseXuiMethod


class GetInbound(BaseXuiMethod):
    async def __call__(self, inbound_id: int) -> Inbound:
        url = self._base_url + f'/panel/api/inbounds/get/{inbound_id}'
        response = await self._session.get(url)
        result = InboundResponse.model_validate(response, by_alias=True)
        return result.obj
