from aiohttp import web
from application.payments import PaymentsService
from infra.rollypay.client import RollyPay
from infra.rollypay.schemas import WebhookCallback


def create_router(payments_service: PaymentsService,
                  rolly_pay: RollyPay):
    router = web.RouteTableDef()

    @router.post('/payment/rollypay')
    async def rollypay(request: web.Request):
        body = await request.json()
        data = WebhookCallback.model_validate(body)
        if not rolly_pay.validate_sign(
            body=body,
            signature=request.headers['X-Signature'],
            timestamp=request.headers['X-Timestamp']
        ):
            return web.Response(body='Invalid Sign', status=403)

        if data.status != 'paid':
            return web.Response(body=f'Status is not "paid". Status is {data.status}', status=400)

        await payments_service.on_payment_webhook(
            metadata=data.metadata
        )
        return web.Response(body='OK', status=200)

    return router
