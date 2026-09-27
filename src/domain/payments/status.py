from enum import Enum, auto


class PaymentStatus(Enum):
    success = auto()
    canceled = auto()
    expired = auto()
