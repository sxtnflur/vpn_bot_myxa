from infra.xui_vpn.clients.get.schemas import GetClientObject, GetClientResponse
from infra.xui_vpn.clients.list.schemas import ClientsListObject, ClientsListResponse
from infra.xui_vpn.shared.base import BaseXuiMethod
from typing_extensions import Literal


class GetClientsList(BaseXuiMethod):
    async def __call__(
            self,
            page: int,
            page_size: int,
            search: Literal['email', 'subId', 'comment'] | None = None,
            filter: Literal['online', 'active', 'deactive', 'depleted'] | None = None,
            sort: Literal['enable', 'email', 'inboundIds', 'traffic', 'remaining', 'expiryTime'] | None = None,
            order: Literal['ascend', 'descend'] | None = None
    ) -> ClientsListObject:
        url = self._base_url + '/panel/api/clients/list/paged'
        params = {
            'page': page,
            'pageSize': page_size
        }
        if search:
            params.update(search=search)
        if filter:
            params.update(filter=filter)
        if sort:
            params.update(sort=sort)
        if order:
            params.update(order=order)

        response = await self._session.get(url, params)
        print(f'Получен ответ: {response}')
        result = ClientsListResponse.model_validate(response, by_alias=True)
        return result.obj
