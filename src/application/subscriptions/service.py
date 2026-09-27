import datetime

from application.errors import ServiceError, IncreaseSubByEmailError
from application.rates import RatesService
from application.subscriptions.dto import Inbound as UserInbound, AddSubscriptionResponse, SubscriptionLinks, \
    Subscription, ExpandedSubscription
from application.subscriptions.inbounds_service import InboundsService
from domain.rates.sub_rate import ProtocolFilter
from infra.xui_vpn import XUIVPN
from infra.xui_vpn.clients.get.schemas import Client
from infra.xui_vpn.shared.schemas import ClientPayload


def rate_id_to_group(rate_id: int):
    return str(rate_id)


def create_client_email(telegram_id: int, rate_id: int) -> str:
    # email в 3x-ui уникален, поэтому у каждого тарифа пользователя свой клиент
    return f'{telegram_id}_{rate_id}'


class SubscriptionsTgBotService:
    def __init__(self, vpn_client: XUIVPN, rates: RatesService, inbounds_service: InboundsService):
        self._vpn_client = vpn_client
        self._rates = rates
        self._inbounds_service = inbounds_service

    @staticmethod
    def _create_comment(full_name: str, username: str | None):
        comment = full_name
        if username:
            comment += f' @{username}'
        return comment

    async def _get_inbounds_ids(self, protocol_filter: ProtocolFilter | None = None) -> list[int]:
        return await self._inbounds_service.get_inbounds_ids(protocol_filter)

    @staticmethod
    def _calc_new_expiry(client: Client, expire_in: datetime.timedelta) -> tuple[int, datetime.datetime | None]:
        """:return: новое значение expiryTime для 3x-ui (мс) и дата окончания (None — бессрочно)"""
        now = datetime.datetime.now(datetime.timezone.utc)
        expire_in_ms = round(expire_in.total_seconds() * 1000)

        if client.is_unlimited:
            # Оплата не должна превращать бессрочного клиента в срочного
            return 0, None

        if client.is_delayed_start:
            # Срок ещё не начался: увеличиваем длительность, отсчёт по-прежнему с первого подключения
            new_expiry = client.expiry_time - expire_in_ms
            return new_expiry, now + datetime.timedelta(milliseconds=-new_expiry)

        new_expire_at = max(client.expire_at, now) + expire_in
        return round(new_expire_at.timestamp() * 1000), new_expire_at

    async def _extend_client(
            self, client: Client, expire_in: datetime.timedelta, **overrides
    ) -> datetime.datetime | None:
        """
        Продлевает клиента, сохраняя все его поля (лимиты, uuid, subId, комментарий)

        :return: новая дата окончания, None — бессрочно
        """
        new_expiry, new_expire_at = self._calc_new_expiry(client, expire_in)
        payload = client.to_client_payload()
        payload.expiry_time = new_expiry
        payload.enable = True
        for field, value in overrides.items():
            setattr(payload, field, value)
        await self._vpn_client.clients.update(client.email, payload)
        return new_expire_at

    async def increase_subscription_by_email(
            self, email: str, expire_in: datetime.timedelta
    ) -> datetime.datetime | None:
        client_obj = await self._vpn_client.clients.get(email)
        if client_obj is None:
            raise IncreaseSubByEmailError('Не найдена подписка')

        return await self._extend_client(client_obj.client, expire_in)

    async def _get_client_by_rate(self, telegram_id: int, rate_id: int) -> Client | None:
        clients = await self._vpn_client.clients.get_by_tg_id(telegram_id)
        group = rate_id_to_group(rate_id)
        for client_obj in clients:
            if client_obj.client.group == group:
                return client_obj.client
        return None

    async def add_subscription(
            self,
            *,
            telegram_id: int,
            full_name: str,
            username: str | None,
            rate_id: int
    ) -> AddSubscriptionResponse:
        rate = self._rates.get_rate(rate_id)
        group = rate_id_to_group(rate_id)
        expire_in = rate.sub_td

        client = await self._get_client_by_rate(telegram_id, rate_id)

        if client:
            new_expire_at = await self._extend_client(
                client, expire_in,
                tg_id=telegram_id,
                group=group,
                comment=client.comment or self._create_comment(full_name, username)
            )
            return AddSubscriptionResponse(
                created=False,
                expire_at=new_expire_at
            )
        else:
            inbounds_ids = await self._get_inbounds_ids(protocol_filter=rate.protocol)
            comment = self._create_comment(full_name, username)

            email = create_client_email(telegram_id, rate_id)
            expire_at = (datetime.datetime.utcnow() + expire_in).replace(tzinfo=datetime.timezone.utc)
            client = ClientPayload(
                email=email,
                tg_id=telegram_id,
                comment=comment,
                expiry_time=round(expire_at.timestamp() * 1000),
                group=group
            )

            await self._vpn_client.clients.add(client, inbound_ids=inbounds_ids)
            return AddSubscriptionResponse(
                created=True,
                expire_at=expire_at
            )

    async def check_if_user_has_sub(self, telegram_id: int) -> bool:
        users = await self._vpn_client.clients.get_by_tg_id(telegram_id)
        now = datetime.datetime.now(datetime.timezone.utc)
        return any(user.client.expire_at is None or user.client.expire_at > now
                   for user in users)

    def get_subscription_link(self, sub_id: str) -> SubscriptionLinks:
        link = self._vpn_client.create_sub_link(sub_id)
        return SubscriptionLinks(
            sub_url=link,
            happ_url='happ://import?url=' + link
        )

    async def get_subscription_links(self, tg_user_id: int) -> list[str]:
        users = await self._vpn_client.clients.get_by_tg_id(tg_user_id)
        user = users[0]
        sub_links = await self._vpn_client.clients.sub_links(user.client.sub_id)
        return sub_links

    # async def _set_group_if_no(self, obj: GetClientObject, rate_id: int):
    #     client = obj.client
    #     if not client.group:
    #         payload = client.to_client_payload()
    #
    #         inbounds = await self._vpn_client.inbounds.options()
    #         protocols = [inb.protocol for inb in inbounds if inb.id in obj.inbound_ids]
    #         payload.group =
    #         await self._vpn_client.clients.update(
    #             email=client.email,
    #             client=payload
    #         )

    async def get_short_subscription(self, telegram_id: int, rate_id: int) -> Subscription | None:
        """
        Получает основную информацию о подписке на конкретный тариф

        :param telegram_id:
        :param rate_id:
        :return:
        """
        subs = await self._vpn_client.clients.get_by_tg_id(telegram_id)
        filtered_subs = list(filter(lambda x: x.client.group == rate_id_to_group(rate_id), subs))
        if not filtered_subs:
            return
        sub = filtered_subs[0]
        return Subscription.from_client(
            email=sub.client.email,
            expire_at=sub.client.expire_at,
            sub_id=sub.client.sub_id,
            comment=sub.client.comment,
            enable=sub.client.enable,
            inbound_ids=sub.inbound_ids,
            group=sub.client.group,
            telegram_id=telegram_id
        )

    async def get_user_subscriptions(self, telegram_id: int) -> list[ExpandedSubscription]:
        subs = await self._vpn_client.clients.get_by_tg_id(telegram_id)
        expanded_subs: list[ExpandedSubscription] = []
        for sub in subs:
            expanded_subs.append(
                await self._expand_sub(
                    Subscription.from_client(
                        email=sub.client.email,
                        expire_at=sub.client.expire_at,
                        sub_id=sub.client.sub_id,
                        comment=sub.client.comment,
                        enable=sub.client.enable,
                        inbound_ids=sub.inbound_ids,
                        group=sub.client.group,
                        telegram_id=sub.client.telegram_id
                    )
                )
            )
        return expanded_subs

    async def get_subscription(self, telegram_id: int, rate_id: int) -> ExpandedSubscription:
        sub = await self.get_short_subscription(telegram_id, rate_id)
        return await self._expand_sub(sub)

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

    async def _expand_sub(self, sub: Subscription) -> ExpandedSubscription:
        """Добавляет к подписке данные: полные inbounds options, traffic, is_online"""

        inbound_options = await self._vpn_client.inbounds.options()
        options_by_id = {option.id: option for option in inbound_options}
        inbounds = [
            UserInbound(id=inbound_id, name=options_by_id[inbound_id].remark,
                        protocol=options_by_id[inbound_id].protocol)
            for inbound_id in sub.inbound_ids
            if inbound_id in options_by_id
        ]
        traffic = await self._vpn_client.clients.traffic(email=sub.email)

        onlines = await self._vpn_client.clients.onlines()

        return ExpandedSubscription(
            email=sub.email,
            expire_at=sub.expire_at,
            sub_id=sub.sub_id,
            active=sub.enable,
            load_down=traffic.down,
            load_up=traffic.up,
            total_gb=traffic.total,
            inbounds=inbounds,
            is_online=sub.email in onlines,
            links=self.get_subscription_link(sub.sub_id)
        )

    async def set_existing_client_rate(self, client: Client, rate_id: int):
        rate = self._rates.get_rate(rate_id)
        inbound_ids = await self._get_inbounds_ids(protocol_filter=rate.protocol)
        exclude_inbound_ids_protocol = (
            rate.protocol.lstrip('!')
            if rate.protocol.startswith('!')
            else ('!' + rate.protocol)
        )
        exclude_inbound_ids = await self._get_inbounds_ids(protocol_filter=exclude_inbound_ids_protocol)
        await self._vpn_client.clients.bulk_attach(
            emails=[client.email], inbound_ids=inbound_ids
        )
        await self._vpn_client.clients.bulk_detach(
            emails=[client.email], inbound_ids=exclude_inbound_ids
        )
        payload = client.to_client_payload()
        payload.group = rate_id_to_group(rate_id)
        await self._vpn_client.clients.update(email=client.email, client=payload)
