from typing import Optional

from infra.xui_vpn.shared.base import BaseXuiMethod
from infra.xui_vpn.shared.schemas import XuiApiResponse

GetLinksResponse = XuiApiResponse[Optional[list[str]]]


class GetLinks(BaseXuiMethod):
    async def __call__(self, sub_id: str) -> Optional[list[str]]:
        url = self._base_url + f'/panel/api/clients/links/{sub_id}'
        response = await self._session.get(url)
        result = GetLinksResponse.model_validate(response)
        return result.obj
