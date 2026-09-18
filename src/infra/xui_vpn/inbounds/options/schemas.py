from pydantic import BaseModel, ConfigDict, Field

from infra.xui_vpn.shared.schemas import XuiApiResponse


class InboundOption(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: int
    remark: str
    tag: str
    protocol: str
    port: int
    enable: bool
    network: str | None = None
    security: str | None = None
    tls_flow_capable: bool = Field(alias='tlsFlowCapable')
    ss_method: str = Field(alias='ssMethod')
    wg_public_key: str | None = Field(alias='wgPublicKey', default=None)
    wg_mtu: int | None = Field(alias='wgMtu', default=None)
    wg_dns: str | None = Field(alias='wgDns', default=None)
    mtproto_domain: str | None = Field(alias='mtprotoDomain', default=None)
    # Protocol-specific server blocks (AmneziaWG/TUIC) — left as raw dicts.
    awg_server: dict | None = Field(alias='awgServer', default=None)
    tuic_server: dict | None = Field(alias='tuicServer', default=None)
    node_id: int | None = Field(alias='nodeId', default=None)
    node_address: str | None = Field(alias='nodeAddress', default=None)
    listen: str | None = None
    share_addr: str | None = Field(alias='shareAddr', default=None)
    share_addr_strategy: str | None = Field(alias='shareAddrStrategy', default=None)


InboundOptionsResponse = XuiApiResponse[list[InboundOption]]
