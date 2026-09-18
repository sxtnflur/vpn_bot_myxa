from infra.xui_vpn.inbounds.options.schemas import InboundOption, InboundOptionsResponse
from infra.xui_vpn.shared.base import BaseXuiMethod


class GetInboundOptions(BaseXuiMethod):
    async def __call__(self) -> list[InboundOption]:
        url = self._base_url + '/panel/api/inbounds/options'
        response = await self._session.get(url)
        result = InboundOptionsResponse.model_validate(response, by_alias=True)
        return result.obj
