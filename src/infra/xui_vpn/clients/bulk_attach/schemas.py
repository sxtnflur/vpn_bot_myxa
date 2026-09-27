from pydantic import BaseModel
from infra.xui_vpn.shared.schemas import XuiApiResponse


class BulkAttachObj(BaseModel):
    attached: list[str] | None
    skipped: list[str] | None
    errors: list[str] | None


BulkAttachResponse = XuiApiResponse[BulkAttachObj]


class BulkDetachObj(BaseModel):
    detached: list[str] | None
    skipped: list[str] | None
    errors: list[str] | None


BulkDetachResponse = XuiApiResponse[BulkDetachObj]
