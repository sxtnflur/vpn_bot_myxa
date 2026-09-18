import datetime
from uuid import UUID

from infra.xui_vpn.shared.schemas import XuiApiResponse
from pydantic import BaseModel, Field
from typing_extensions import Generic


class ClientTraffic(BaseModel):
    id: int
    inbound_id: int = Field(alias='inboundId')
    enable: bool
    email: str
    uuid: str
    sub_id: str = Field(alias='subId')
    up: int
    down: int
    expiry_time: datetime.datetime = Field(alias='expiryTime')
    total: int
    reset: int
    reset_day: int = Field(alias='resetDay')
    reset_max: int = Field(alias='resetMax')
    reset_count: int = Field(alias='resetCount')
    last_online: datetime.datetime = Field(alias='lastOnline')
    lasy_sub_fetch: datetime.datetime = Field(alias='lastSubFetch')


class ListClient(BaseModel):
    email: str
    sub_id: str = Field(alias='subId')
    enable: bool
    total_gb: int = Field(alias='totalGB')
    expiry_time: datetime.datetime = Field(alias='expiryTime')
    limit_ip: int = Field(alias='limitIp')
    limit_hwid: int = Field(alias='limitHwid')
    reset: int
    reset_day: int = Field(alias='resetDay')
    reset_max: int = Field(alias='resetMax')
    comment: str | None = None
    inbound_ids: list[int] = Field(alias='inboundIds')
    traffic: ClientTraffic
    created_at: datetime.datetime = Field(alias='createdAt')
    updated_at: datetime.datetime = Field(alias='updatedAt')


class ClientsListObject(BaseModel):
    items: list[ListClient]




ClientsListResponse = XuiApiResponse[ClientsListObject]

