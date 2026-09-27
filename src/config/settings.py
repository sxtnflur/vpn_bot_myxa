import datetime

from pydantic.v1 import BaseSettings
from typing_extensions import Literal


class Settings(BaseSettings):
    xui_api_key: str
    xui_api_url: str
    xui_sub_base_url: str

    bot_token: str

    yookassa_shop_id: str
    yookassa_secret_key: str

    rollypay_api_key: str
    rollypay_secret_webhook: str
    rollypay_base_url: str = 'https://rollypay.io'

    bot_url: str
    support_url: str
    privacy_policy_url: str
    user_agreement_url: str

    admin_log_chat_id: int

    webhook_url: str | None = None
    webhook_secret: str | None = None

    tz: datetime.timedelta = datetime.timedelta(hours=3)

    # Если не задан — кэш и FSM хранятся в памяти и теряются при рестарте
    redis_url: str | None = None

    log_level: Literal['DEBUG', 'INFO', 'WARN', 'ERROR'] = 'DEBUG'
    # Без значения по умолчанию: тестовый режим раздаёт подписки бесплатно, его нужно указывать явно
    test_payment: bool

    class Config:
        case_sensitive = False


class WebhookSettings(Settings):
    webhook_url: str  # без app_prefix и /webhook
    port: int
    webhook_secret: str | None = None
    app_prefix: str = '/vpnmyxa'

    class Config:
        case_sensitive = False
