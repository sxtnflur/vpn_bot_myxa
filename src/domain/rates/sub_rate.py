import datetime
from dataclasses import dataclass
from typing_extensions import Literal


@dataclass(frozen=True)
class SubRate:
    id: int
    name: str
    price: int
    protocol: Literal['wireguard', 'vless']
    sub_td: datetime.timedelta
