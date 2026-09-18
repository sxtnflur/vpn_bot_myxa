from infra.xui_vpn.inbounds.list.schemas import Inbound, InboundsListResponse
from infra.xui_vpn.shared.base import BaseXuiMethod


class GetInboundsListSlim(BaseXuiMethod):
    """List-page variant: settings.clients[] entries are stripped of secrets."""

    async def __call__(self) -> list[Inbound]:
        url = self._base_url + '/panel/api/inbounds/list/slim'
        response = await self._session.get(url)
        result = InboundsListResponse.model_validate(response, by_alias=True)
        return result.obj
