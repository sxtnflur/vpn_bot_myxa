from dataclasses import dataclass


@dataclass
class PaymentResult:
    id: str
    url: str


@dataclass
class CreatedPayment:
    url: str
