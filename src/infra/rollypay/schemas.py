import datetime

from pydantic import BaseModel
from typing_extensions import Literal


Status = Literal['created', 'processing', 'paid',
                 'expired', 'canceled',
                 'chargeback', 'refunded']


class PaymentResponse(BaseModel):
    payment_id: str
    order_id: str
    status: Status
    token: str
    pay_url: str
    amount: float
    payment_currency: str
    qr_content: str | None = None
    h2h_enabled: bool
    qr_activated: bool
    created_at: datetime.datetime
    expires_at: datetime.datetime


class WebhookCallback(BaseModel):
    event_type: str
    payment_id: str
    order_id: str
    amount: float
    currency: str
    test: bool
    metadata: dict | None = None
