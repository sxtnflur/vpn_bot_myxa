from pydantic import BaseModel, ConfigDict, Field

from infra.xui_vpn.shared.schemas import ClientPayload, XuiApiSimpleResponse


class AddClientRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    client: ClientPayload
    inbound_ids: list[int] = Field(alias='inboundIds')


AddClientResponse = XuiApiSimpleResponse
