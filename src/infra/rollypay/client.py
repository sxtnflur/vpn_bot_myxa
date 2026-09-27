import hashlib
import hmac
import uuid

from infra.client.session.base import BaseSession
from infra.rollypay.schemas import PaymentResponse
from typing_extensions import Literal


class RollyPay:
    def __init__(
            self,
            api_key: str,
            base_url: str,
            secret_webhook: str,
            session: BaseSession,
            redirect_url: str | None = None
    ):
        self._api_key = api_key
        self._base_url = base_url
        self._secret_webhook = secret_webhook
        self._redirect_url = redirect_url
        self._session = session

    def validate_sign(
            self,
            body: bytes | str,
            timestamp: str | None,
            signature: str | None
    ) -> bool:
        if not timestamp or not signature:
            return False
        if isinstance(body, str):
            body = body.encode()

        expected = hmac.new(
            self._secret_webhook.encode(),
            timestamp.encode() + b'.' + body,
            hashlib.sha256
        ).hexdigest()

        return hmac.compare_digest(expected, signature)

    def _create_headers(self):
        return {
            'X-API-Key': self._api_key,
            'X-Nonce': str(uuid.uuid4())
        }

    async def create_payment(
            self,
            *,
            amount: float,
            description: str,
            payment_method: Literal['sbp', 'card', 'intl_card', 'crypto'] = 'sbp',
            metadata: dict | None = None,
            test: bool = False
    ) -> PaymentResponse:
        data = {
            'amount': str(float(amount)),
            'payment_currency': 'RUB',
            'payment_method': payment_method,
            'order_id': str(uuid.uuid4()),
            'description': description,
            'test': test
        }
        if self._redirect_url:
            data.update(redirect_url=self._redirect_url)
        if metadata:
            data.update(metadata=metadata)

        headers = self._create_headers()

        result = await self._session.post(
            url=self._base_url + '/api/v1/payments',
            data=data,
            headers=headers
        )
        result = PaymentResponse.model_validate(result)
        return result

    async def set_webhook_url(
            self,
            webhook_url: str,
            terminal_id: str
    ):
        response = await self._session.post(
            url=self._base_url + '/api/v1/terminals/' + terminal_id,
            data={'callback_url': webhook_url}
        )
        print(f'{response=}')
