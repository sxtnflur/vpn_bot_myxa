import datetime
from dataclasses import dataclass

from typing_extensions import Literal



@dataclass(frozen=True)
class Inbound:
    id: int
    name: str

    @property
    def full_name(self):
        return f'#{self.id} {self.name}'


@dataclass(frozen=True)
class User:
    email: str
    expire_at: datetime.datetime
    sub_id: int
    active: bool
    load_up: int
    load_down: int
    total_gb: int
    updated_at: datetime.datetime
    inbounds: list[Inbound]
    is_online: bool
    traffic_reset: Literal['never']
    comment: str | None = None


@dataclass(frozen=True)
class AddSubscriptionResponse:
    created: bool
    expire_at: datetime.datetime


@dataclass(frozen=True)
class SubscriptionLinks:
    sub_url: str
    happ_url: str
