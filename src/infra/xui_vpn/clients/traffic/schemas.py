import datetime

from pydantic import BaseModel, Field

from infra.xui_vpn.shared.schemas import XuiApiResponse


class Traffic(BaseModel):
    email: str
    up: int
    down: int
    total: int
    expiry_time: datetime.datetime = Field(alias='expiryTime')


TrafficResponse = XuiApiResponse[Traffic]
