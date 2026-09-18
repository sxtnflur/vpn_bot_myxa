from infra.xui_vpn.clients.get.schemas import GetClientObject
from infra.xui_vpn.shared.schemas import XuiApiResponse

GetClientsByTgIdResponse = XuiApiResponse[list[GetClientObject]]
