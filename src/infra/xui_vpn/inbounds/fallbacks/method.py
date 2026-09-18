from infra.xui_vpn.inbounds.fallbacks.schemas import InboundFallback, InboundFallbacksResponse
from infra.xui_vpn.shared.base import BaseXuiMethod


class GetInboundFallbacks(BaseXuiMethod):
    async def __call__(self, inbound_id: int) -> list[InboundFallback]:
        url = self._base_url + f'/panel/api/inbounds/{inbound_id}/fallbacks'
        response = await self._session.get(url)
        result = InboundFallbacksResponse.model_validate(response, by_alias=True)
        return result.obj
