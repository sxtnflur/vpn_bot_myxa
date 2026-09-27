from application.subscriptions.dto import Subscription
from application.subscriptions.inbounds_service import InboundsService
from infra.xui_vpn import XUIVPN


class SubscriptionByEmailService:
    def __init__(self, vpn_client: XUIVPN, inbounds_service: InboundsService):
        self._vpn_client = vpn_client
        self._inbounds = inbounds_service

    async def get_subscription_by_email(self, email: str) -> Subscription | None:
        sub = await self._vpn_client.clients.get(email)
        if sub is None:
            return

        return Subscription.from_client(
            email=email,
            sub_id=sub.client.sub_id,
            expire_at=sub.client.expire_at,
            enable=sub.client.enable,
            inbound_ids=sub.inbound_ids,
            telegram_id=sub.client.telegram_id
        )

    async def get_subscription_amount_by_sub(self, sub: Subscription) -> int:
        protocols = set()
        for inbound in await self._inbounds.get_inbounds():
            if inbound.id in sub.inbound_ids:
                protocols.add(inbound.protocol)

        if not protocols:
            raise ValueError('Inbounds не найдены')

        amount = 0
        if 'wireguard' in protocols:
            amount += 500
        else:
            amount += 200
        return amount
