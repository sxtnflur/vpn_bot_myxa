from domain.payments.payment_service import PaymentService


class PaymentsRegistry:
    def __init__(self):
        self._payments = {}

    def add(self, key: str, service: PaymentService) -> 'PaymentsRegistry':
        self._payments[key] = service
        return self

    def get(self, key: str) -> PaymentService:
        return self._payments[key]
