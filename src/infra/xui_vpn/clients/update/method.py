from infra.xui_vpn.clients.update.schemas import UpdateClientResponse
from infra.xui_vpn.shared.base import BaseXuiMethod
from infra.xui_vpn.shared.exceptions import XuiApiError
from infra.xui_vpn.shared.schemas import ClientPayload


class UpdateClient(BaseXuiMethod):
    async def __call__(self, email: str, client: ClientPayload) -> None:
        url = self._base_url + f'/panel/api/clients/update/{email}'
        response = await self._session.post(url, data=client.model_dump(by_alias=True, exclude_none=True))
        print(f'{response=}')
        result = UpdateClientResponse.model_validate(response, by_alias=True)
        if not result.success:
            raise XuiApiError(result.msg)
