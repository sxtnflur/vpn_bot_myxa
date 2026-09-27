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
    expiry_time: datetime.datetime = Field(alias='expiryTime')
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

    def to_client_payload(self):
        return ClientPayload(
            email=self.email,
            sub_id=self.sub_id,
            uuid=str(self.uuid),
            total_gb=self.total_gb,
            expiry_time=round(self.expiry_time.timestamp()),
            tg_id=self.telegram_id,
            limit_id=self.limit_ip,
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


GetClientResponse = XuiApiResponse[GetClientObject]
