from infra.xui_vpn.clients.add.schemas import AddClientRequest, AddClientResponse
from infra.xui_vpn.shared.base import BaseXuiMethod
from infra.xui_vpn.shared.exceptions import ClientAlreadyExistsError, XuiApiError
from infra.xui_vpn.shared.schemas import ClientPayload


class AddClient(BaseXuiMethod):
    async def __call__(self, client: ClientPayload, inbound_ids: list[int]) -> None:
        url = self._base_url + '/panel/api/clients/add'
        payload = AddClientRequest(client=client, inbound_ids=inbound_ids)
        response = await self._session.post(url, data=payload.model_dump(by_alias=True, exclude_none=True))
        print(f'{response=}')
        result = AddClientResponse.model_validate(response, by_alias=True)
        if not result.success:
            if 'already in use' in result.msg:
                raise ClientAlreadyExistsError(result.msg)
            raise XuiApiError(result.msg)
