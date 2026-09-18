from infra.xui_vpn.clients.traffic.schemas import TrafficResponse, Traffic
from infra.xui_vpn.shared.base import BaseXuiMethod


class GetTraffic(BaseXuiMethod):
    async def __call__(self, email: str) -> Traffic:
        url = self._base_url + f'/panel/api/clients/traffic/{email}'
        response = await self._session.get(url)
        result = TrafficResponse.model_validate(response, by_alias=True)
        return result.obj
