from infra.xui_vpn.clients.delete.schemas import DeleteClientResponse
from infra.xui_vpn.shared.base import BaseXuiMethod


class DeleteClient(BaseXuiMethod):
    async def __call__(self, email: str, keep_traffic: bool = False) -> None:
        url = self._base_url + f'/panel/api/clients/del/{email}'
        params = {'keepTraffic': 1} if keep_traffic else None
        response = await self._session.post(url, params=params)
        print(f'{response=}')
        result = DeleteClientResponse.model_validate(response, by_alias=True)
