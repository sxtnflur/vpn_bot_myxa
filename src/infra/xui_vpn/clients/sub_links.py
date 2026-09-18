from infra.xui_vpn.shared.base import BaseXuiMethod
from infra.xui_vpn.shared.schemas import XuiApiResponse


GetSubLinksResponse = XuiApiResponse[list[str]]


class GetSubLinks(BaseXuiMethod):
    async def __call__(self, sub_id: str) -> list[str]:
        url = self._base_url + f'/panel/api/clients/subLinks/{sub_id}'
        response = await self._session.get(url)
        result = GetSubLinksResponse.model_validate(response)
        return result.obj
