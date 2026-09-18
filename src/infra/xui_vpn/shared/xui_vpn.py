from infra.client.session.base import BaseSession
from infra.xui_vpn.clients.methods import ClientsMethods
from infra.xui_vpn.inbounds.methods import InboundsMethods


class XUIVPN:
    def __init__(
            self,
            base_url: str,
            api_key: str,
            sub_base_url: str,
            session: BaseSession
    ):
        self.clients = ClientsMethods(base_url=base_url, api_key=api_key, session=session)
        self.inbounds = InboundsMethods(base_url=base_url, api_key=api_key, session=session)

        self._sub_base_url = sub_base_url

    def create_sub_link(self, sub_id: str):
        return self._sub_base_url + '/' + sub_id
