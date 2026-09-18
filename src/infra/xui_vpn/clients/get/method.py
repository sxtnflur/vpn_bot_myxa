from infra.xui_vpn.clients.get.schemas import GetClientObject, GetClientResponse
from infra.xui_vpn.shared.base import BaseXuiMethod


class GetClient(BaseXuiMethod):
    async def __call__(self, email: str) -> GetClientObject:
        url = self._base_url + f'/panel/api/clients/get/{email}'
        response = await self._session.get(url)
        print(f'{response=}')
        result = GetClientResponse.model_validate(response, by_alias=True)
        return result.obj
