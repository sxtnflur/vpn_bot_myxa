import datetime
from uuid import UUID

from infra.xui_vpn.shared.schemas import XuiApiResponse, ClientPayload
from pydantic import Field, BaseModel


class Client(BaseModel):
    id: int
    email: str
    sub_id: str = Field(alias='subId')
    uuid: UUID
    # password: str
    # auth: str
    # flow: str | None = None
    # security: str | None = 'auto'
    # private_key: str = Field(alias='privateKey')
    # public_key: str = Field(alias='publicKey')
    # allowed_ips: str = Field(alias='allowedIPs')
    # secret: str
    limit_ip: int = Field(alias='limitIp')
    total_gb: int = Field(alias='totalGB')
    # Сырое значение 3x-ui в мс: 0 — бессрочно, < 0 — срок (в мс) начнётся с первого подключения
    expiry_time: int = Field(alias='expiryTime')
    enable: bool
    telegram_id: int = Field(alias='tgId')
    group: str | None = None
    comment: str | None = None
    reset: int
    reset_day: int = Field(alias='resetDay')
    reset_max: int = Field(alias='resetMax')
    traffic_reset: str | None = Field(alias='trafficReset', default=None)
    traffic_reset_day: int | None = Field(alias='trafficResetDay', default=None)
    created_at: datetime.datetime = Field(alias='createdAt')
    updated_at: datetime.datetime = Field(alias='updatedAt')

    @property
    def is_unlimited(self) -> bool:
        return self.expiry_time == 0

    @property
    def is_delayed_start(self) -> bool:
        return self.expiry_time < 0

    @property
    def expire_at(self) -> datetime.datetime | None:
        """
        Дата окончания в UTC. None — бессрочно.
        Для отложенного старта — оценка: если подключиться сейчас
        """
        if self.is_unlimited:
            return None
        if self.is_delayed_start:
            return datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(milliseconds=-self.expiry_time)
        return datetime.datetime.fromtimestamp(self.expiry_time / 1000, tz=datetime.timezone.utc)

    def to_client_payload(self):
        return ClientPayload(
            email=self.email,
            sub_id=self.sub_id,
            uuid=str(self.uuid),
            total_gb=self.total_gb,
            expiry_time=self.expiry_time,
            tg_id=self.telegram_id,
            limit_ip=self.limit_ip,
            enable=self.enable,
            group=self.group,
            comment=self.comment,
            reset_day=self.reset_day,
            reset_max=self.reset_max
        )


class GetClientObject(BaseModel):
    client: Client
    inbound_ids: list[int] = Field(alias='inboundIds')
    used_traffic: int = Field(alias='usedTraffic')


class GetClientResponse(BaseModel):
    # Для несуществующего клиента 3x-ui отвечает success=false и obj=null
    success: bool
    msg: str
    obj: GetClientObject | None = None
