from infra.xui_vpn.shared.base import BaseXuiMethod
from infra.xui_vpn.clients.bulk_attach.schemas import BulkAttachResponse, BulkDetachResponse


class BulkAttachClient(BaseXuiMethod):
    async def __call__(self, emails: list[str], inbound_ids: list[str]) -> BulkAttachResponse:
        url = self._base_url + '/panel/api/clients/bulkAttach'
        response = await self._session.post(url, data={'emails': emails, 'inboundIds': inbound_ids})
        print(f'{response=}')
        result = BulkAttachResponse.model_validate(response, by_alias=True)
        return result.obj


class BulDetachClient(BaseXuiMethod):
    async def __call__(self, emails: list[str], inbound_ids: list[str]) -> BulkDetachResponse:
        url = self._base_url + '/panel/api/clients/bulkDetach'
        response = await self._session.post(url, data={'emails': emails, 'inboundIds': inbound_ids})
        print(f'{response=}')
        result = BulkDetachResponse.model_validate(response, by_alias=True)
        return result.obj
