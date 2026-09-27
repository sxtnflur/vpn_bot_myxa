import datetime
from dataclasses import dataclass
from typing_extensions import Literal


ProtocolFilter = Literal['wireguard', 'vless', '!wireguard', '!vless']  # ! - означает все кроме этого протокола


@dataclass(frozen=True)
class SubRate:
    id: int
    name: str
    price: int
    protocol: ProtocolFilter | None
    sub_td: datetime.timedelta
