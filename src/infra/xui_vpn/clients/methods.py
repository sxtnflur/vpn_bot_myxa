from infra.client.session.base import BaseSession
from infra.xui_vpn.clients.llinks import GetLinks
from infra.xui_vpn.clients.onlines import GetOnlineEmails
from infra.xui_vpn.clients.sub_links import GetSubLinks
from infra.xui_vpn.clients.traffic import GetTraffic
from infra.xui_vpn.shared.base import BaseXuiMethods
from infra.xui_vpn.clients.list import GetClientsList
from infra.xui_vpn.clients.get import GetClient
from infra.xui_vpn.clients.get_by_tg_id import GetClientsByTgId
from infra.xui_vpn.clients.add import AddClient
from infra.xui_vpn.clients.update import UpdateClient
from infra.xui_vpn.clients.delete import DeleteClient


class ClientsMethods(BaseXuiMethods):
    def __init__(self, base_url: str, api_key: str, session: BaseSession):
        self.list = GetClientsList(base_url, api_key, session)
        self.get = GetClient(base_url, api_key, session)
        self.get_by_tg_id = GetClientsByTgId(base_url, api_key, session)
        self.add: AddClient = AddClient(base_url, api_key, session)
        self.update = UpdateClient(base_url, api_key, session)
        self.delete = DeleteClient(base_url, api_key, session)
        self.sub_links = GetSubLinks(base_url, api_key, session)
        self.links = GetLinks(base_url, api_key, session)
        self.traffic = GetTraffic(base_url, api_key, session)
        self.onlines = GetOnlineEmails(base_url, api_key, session)
        super().__init__(base_url, api_key, session)
