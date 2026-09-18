import datetime

from application.subscriptions.dto import Inbound as UserInbound, AddSubscriptionResponse, SubscriptionLinks
from application.subscriptions.dto import User
from infra.xui_vpn import XUIVPN
from infra.xui_vpn.shared.schemas import ClientPayload


class SubscriptionsTgBotService:
    def __init__(self, vpn_client: XUIVPN):
        self._vpn_client = vpn_client

    @staticmethod
    def _create_comment(full_name: str, username: str | None):
        comment = full_name
        if username:
            comment += f' @{username}'
        return full_name

    async def _get_inbounds_ids(self) -> list[int]:
        inbounds = await self._vpn_client.inbounds.options()
        return list(map(lambda inbound: inbound.id, inbounds))

    async def add_subscription(
            self,
            *,
            telegram_id: int,
            full_name: str,
            username: str | None,
            expire_in: datetime.timedelta
    ) -> AddSubscriptionResponse:
        if expire_in < datetime.timedelta(seconds=0):
            raise ValueError('expire_at must be more than 1 second')

        user = await self.get_subscription(telegram_id)

        if user:
            new_expire_at = (user.expire_at + expire_in).replace(tzinfo=datetime.timezone.utc)
            await self._vpn_client.clients.update(
                user.email,
                ClientPayload(
                    email=user.email,
                    tg_id=telegram_id,
                    comment=user.comment or self._create_comment(full_name, username),
                    expiry_time=round(new_expire_at.timestamp() * 1000)
                )
            )
            return AddSubscriptionResponse(
                created=False,
                expire_at=new_expire_at
            )
        else:
            inbounds_ids = await self._get_inbounds_ids()
            comment = self._create_comment(full_name, username)

            email = str(telegram_id)
            expire_at = (datetime.datetime.utcnow() + expire_in).replace(tzinfo=datetime.timezone.utc)
            client = ClientPayload(
                email=email,
                tg_id=telegram_id,
                comment=comment,
                expiry_time=round(expire_at.timestamp() * 1000)
            )

            await self._vpn_client.clients.add(client, inbound_ids=inbounds_ids)
            return AddSubscriptionResponse(
                created=True,
                expire_at=expire_at
            )

    async def check_if_user_has_sub(self, telegram_id: int) -> bool:
        user = await self._vpn_client.clients.get_by_tg_id(telegram_id)
        return user.client.expiry_time < datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc)

    async def get_subscription_link(self, telegram_id: int) -> SubscriptionLinks:
        user = await self._vpn_client.clients.get_by_tg_id(telegram_id)
        link = self._vpn_client.create_sub_link(user.client.sub_id)
        return SubscriptionLinks(
            sub_url=link,
            happ_url='happ://import?url=' + link
        )

    async def get_subscription_links(self, tg_user_id: int) -> list[str]:
        user = await self._vpn_client.clients.get_by_tg_id(tg_user_id)
        sub_links = await self._vpn_client.clients.sub_links(user.client.sub_id)
        return sub_links

    async def get_subscription(self, telegram_id: int) -> User:
        vpn_user = await self._vpn_client.clients.get_by_tg_id(telegram_id)
        print(f'{vpn_user.client.traffic_reset=}')
        expire_at = vpn_user.client.expiry_time
        if expire_at.tzinfo is not None:
            expire_at = expire_at.astimezone(datetime.timezone.utc).replace(tzinfo=None)

        inbound_options = await self._vpn_client.inbounds.options()
        options_by_id = {option.id: option for option in inbound_options}
        inbounds = [
            UserInbound(id=inbound_id, name=options_by_id[inbound_id].remark)
            for inbound_id in vpn_user.inbound_ids
            if inbound_id in options_by_id
        ]
        traffic = await self._vpn_client.clients.traffic(email=vpn_user.client.email)

        onlines = await self._vpn_client.clients.onlines()

        return User(
            email=vpn_user.client.email,
            expire_at=expire_at,
            sub_id=vpn_user.client.sub_id,
            active=vpn_user.client.enable,
            load_down=traffic.down,
            load_up=traffic.up,
            total_gb=traffic.total,
            updated_at=vpn_user.client.updated_at,
            inbounds=inbounds,
            is_online=vpn_user.client.email in onlines,
            traffic_reset=vpn_user.client.traffic_reset
        )
