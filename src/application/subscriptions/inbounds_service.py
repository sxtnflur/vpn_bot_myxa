from application.subscriptions.dto import Inbound
from domain.rates.sub_rate import ProtocolFilter
from infra.xui_vpn import XUIVPN


class InboundsService:
    def __init__(self, vpn_client: XUIVPN):
        self._vpn_client = vpn_client

    async def get_inbounds(self) -> list[Inbound]:
        inbounds = await self._vpn_client.inbounds.options()
        return list(map(lambda inbound: Inbound(
            id=inbound.id,
            name=inbound.remark,
            protocol=inbound.protocol
        ), inbounds))

    async def get_inbounds_ids(self, protocol_filter: ProtocolFilter | None = None) -> list[int]:
        inbounds = await self._vpn_client.inbounds.options()

        if protocol_filter:
            if protocol_filter.startswith('!'):
                inbounds = list(filter(
                    lambda inbound: inbound.protocol != protocol_filter.lstrip('!'), inbounds
                ))
            else:
                inbounds = list(filter(
                    lambda inbound: inbound.protocol == protocol_filter, inbounds
                ))

        return list(map(lambda inbound: inbound.id, inbounds))