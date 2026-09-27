import datetime
from dataclasses import dataclass

from typing_extensions import Literal


@dataclass(frozen=True)
class Inbound:
    id: int
    name: str
    protocol: str

    @property
    def full_name(self):
        return f'#{self.id} {self.name}'


@dataclass
class Subscription:
    email: str
    telegram_id: int | None
    expire_at: datetime.datetime | None  # None — бессрочно
    sub_id: str
    rate_id: int | None
    enable: bool
    inbound_ids: list[int]
    comment: str | None

    def __post_init__(self) -> None:
        if self.expire_at is not None and self.expire_at.tzinfo is not None:
            self.expire_at = self.expire_at.astimezone(datetime.timezone.utc).replace(tzinfo=None)

    @classmethod
    def from_client(
            cls,
            email: str,
            telegram_id: int | None,
            expire_at: datetime.datetime | None,
            sub_id: str,
            enable: bool,
            inbound_ids: list[int],
            comment: str | None = None,
            group: str | None = None
    ):
        return cls(
            email=email,
            expire_at=expire_at,
            sub_id=sub_id,
            comment=comment,
            enable=enable,
            inbound_ids=inbound_ids,
            rate_id=int(group) if group and group.isdigit() else None,
            telegram_id=telegram_id
        )


@dataclass(frozen=True)
class User:
    email: str
    expire_at: datetime.datetime | None  # None — бессрочно
    sub_id: str
    active: bool
    load_up: int
    load_down: int
    total_gb: int
    inbounds: list[Inbound]
    is_online: bool
    links: 'SubscriptionLinks'
    traffic_reset: Literal['never'] = 'never'
    comment: str | None = None


ExpandedSubscription = User


@dataclass(frozen=True)
class AddSubscriptionResponse:
    created: bool
    expire_at: datetime.datetime | None  # None — бессрочно
    email: str | None = None  # email созданного клиента


@dataclass(frozen=True)
class SubscriptionLinks:
    sub_url: str
    happ_url: str


@dataclass(frozen=True)
class SubscriptionsPage:
    items: list[ExpandedSubscription]
    page: int  # с 0
    pages: int  # всегда >= 1, даже если подписок нет
    total: int
    offset: int  # индекс первой подписки страницы среди всех подписок пользователя

    @property
    def has_prev(self) -> bool:
        return self.page > 0

    @property
    def has_next(self) -> bool:
        return self.page < self.pages - 1
