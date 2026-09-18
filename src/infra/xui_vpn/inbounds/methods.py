from infra.client.session.base import BaseSession
from infra.xui_vpn.shared.base import BaseXuiMethods

from infra.xui_vpn.inbounds.get import GetInbound
from infra.xui_vpn.inbounds.all_links import GetAllInboundLinks
from infra.xui_vpn.inbounds.fallbacks import GetInboundFallbacks
from infra.xui_vpn.inbounds.list import GetInboundsList
from infra.xui_vpn.inbounds.list_slim import GetInboundsListSlim
from infra.xui_vpn.inbounds.options import GetInboundOptions


class InboundsMethods(BaseXuiMethods):
    def __init__(self, base_url: str, api_key: str, session: BaseSession):
        self.get = GetInbound(base_url, api_key, session)
        self.all_links = GetAllInboundLinks(base_url, api_key, session)
        self.fallbacks = GetInboundFallbacks(base_url, api_key, session)
        self.list = GetInboundsList(base_url, api_key, session)
        self.list_slim = GetInboundsListSlim(base_url, api_key, session)
        self.options = GetInboundOptions(base_url, api_key, session)
        super().__init__(base_url, api_key, session)
