from pydantic import BaseModel, ConfigDict, Field
from typing_extensions import Generic, TypeVar

T = TypeVar('T')


class XuiApiResponse(BaseModel, Generic[T]):
    success: bool
    msg: str
    obj: T


class XuiApiSimpleResponse(BaseModel):
    """Response for endpoints that don't return an `obj` payload (add/update/del)."""
    success: bool
    msg: str


class ClientPayload(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    email: str
    sub_id: str | None = Field(alias='subId', default=None)
    uuid: str | None = None
    total_gb: int = Field(alias='totalGB', default=0)
    expiry_time: int = Field(alias='expiryTime', default=0)
    tg_id: int | None = Field(alias='tgId', default=None)
    limit_ip: int = Field(alias='limitIp', default=0)
    enable: bool = True
    group: str | None = None
    comment: str | None = None
    reset_day: int | None = Field(alias='resetDay', default=None)
    reset_max: int | None = Field(alias='resetMax', default=None)


# class UpdateClientPayload(ClientPayload):
#     email: str
#     sub_id: str | None = Field(alias='subId', default=None)
#     uuid: str | None = None
#     total_gb: int | None = Field(alias='totalGB', default=None)
#     expiry_time: int | None = Field(alias='expiryTime', default=None)
#     tg_id: int | None = Field(alias='tgId', default=None)
#     limit_ip: int | None = Field(alias='limitIp', default=None)
#     enable: bool | None = None
#     group: str | None = None
#     comment: str | None = None
#     reset_day: int | None = Field(alias='resetDay', default=None)
#     reset_max: int | None = Field(alias='resetMax', default=None)
