from infra.xui_vpn.shared.base import BaseXuiMethod
from infra.xui_vpn.shared.schemas import XuiApiResponse


class GetAllInboundLinks(BaseXuiMethod):
    async def __call__(self) -> list[str]:
        url = self._base_url + '/panel/api/inbounds/allLinks'
        response = await self._session.get(url)
        result = XuiApiResponse[list[str]].model_validate(response, by_alias=True)
        return result.obj
