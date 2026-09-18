from pydantic import BaseModel, ConfigDict, Field

from infra.xui_vpn.shared.schemas import XuiApiResponse


class InboundFallback(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: int
    master_id: int = Field(alias='masterId')
    child_id: int = Field(alias='childId')
    name: str
    alpn: str
    path: str
    dest: str
    xver: int
    sort_order: int = Field(alias='sortOrder')


InboundFallbacksResponse = XuiApiResponse[list[InboundFallback]]
