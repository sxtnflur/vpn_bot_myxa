from pydantic import BaseModel, ConfigDict, Field

from infra.xui_vpn.clients.list.schemas import ClientTraffic
from infra.xui_vpn.shared.schemas import XuiApiResponse


class FallbackParentInfo(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    master_id: int = Field(alias='masterId')
    path: str | None = None


class Inbound(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: int
    up: int
    down: int
    total: int
    remark: str
    sub_sort_index: int = Field(alias='subSortIndex')
    enable: bool
    expiry_time: int = Field(alias='expiryTime')
    traffic_reset: str = Field(alias='trafficReset')
    traffic_reset_day: int = Field(alias='trafficResetDay')
    last_traffic_reset_time: int = Field(alias='lastTrafficResetTime')
    client_stats: list[ClientTraffic] = Field(alias='clientStats', default_factory=list)
    listen: str
    port: int
    protocol: str
    # Raw Xray JSON blobs (shape differs per protocol) — left unparsed on purpose.
    settings: dict
    stream_settings: dict = Field(alias='streamSettings')
    sniffing: dict
    tag: str
    node_id: int | None = Field(alias='nodeId', default=None)
    share_addr_strategy: str = Field(alias='shareAddrStrategy')
    share_addr: str = Field(alias='shareAddr')
    disable_flow: bool = Field(alias='disableFlow')
    origin_node_guid: str | None = Field(alias='originNodeGuid', default=None)
    fallback_parent: FallbackParentInfo | None = Field(alias='fallbackParent', default=None)


InboundsListResponse = XuiApiResponse[list[Inbound]]
