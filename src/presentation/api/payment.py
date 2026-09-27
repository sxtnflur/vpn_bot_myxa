import logging

from aiohttp import web
from application.payments import PaymentsService
from infra.rollypay.client import RollyPay
from infra.rollypay.schemas import WebhookCallback
from pydantic import ValidationError


def create_router(payments_service: PaymentsService,
                  rolly_pay: RollyPay,
                  accept_test: bool = False):
    """
    :param accept_test: принимать тестовые платежи (test=true). В проде должно быть False
    """
    router = web.RouteTableDef()

    @router.post('/payment/rollypay')
    async def rollypay(request: web.Request):
        # Подпись считается от сырого тела: timestamp + "." + body
        raw_body = await request.read()
        if not rolly_pay.validate_sign(
            body=raw_body,
            signature=request.headers.get('X-Signature'),
            timestamp=request.headers.get('X-Timestamp')
        ):
            return web.Response(text='Invalid Sign', status=403)

        try:
            data = WebhookCallback.model_validate_json(raw_body)
        except ValidationError:
            logging.exception('RollyPay: невалидное тело вебхука: %r', raw_body)
            return web.Response(text='Invalid body', status=400)

        if data.test and not accept_test:
            logging.warning('RollyPay: тестовый платёж %s отклонён (TEST_PAYMENT=false)', data.payment_id)
            return web.Response(text='Test payments are disabled', status=200)

        if not data.metadata:
            logging.error('RollyPay: оплата %s без metadata', data.payment_id)
            return web.Response(text='No metadata', status=200)

        logging.info(f'Новый платеж: {data}')

        await payments_service.on_payment_webhook(
            payment_id=data.payment_id,
            metadata=data.metadata,
            is_succeed=data.status not in ('canceled', 'expired')
        )
        return web.Response(text='OK', status=200)

    return router
