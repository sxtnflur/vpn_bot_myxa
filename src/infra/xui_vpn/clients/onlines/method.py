from infra.xui_vpn.clients.onlines.schemas import GetOnlineEmailsResponse
from infra.xui_vpn.shared.base import BaseXuiMethod


class GetOnlineEmails(BaseXuiMethod):
    async def __call__(self) -> list[str]:
        url = self._base_url + '/panel/api/clients/onlines'
        response = await self._session.post(url)
        result = GetOnlineEmailsResponse.model_validate(response, by_alias=True)
        return result.obj
