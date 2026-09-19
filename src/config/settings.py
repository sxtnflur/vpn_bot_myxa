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

    bot_url: str
    support_url: str
    privacy_policy_url: str
    user_agreement_url: str

    webhook_url: str | None = None
    webhook_secret: str | None = None

    tz: datetime.timedelta = datetime.timedelta(hours=3)

    log_level: Literal['DEBUG', 'INFO', 'WARN', 'ERROR'] = 'DEBUG'

    class Config:
        case_sensitive = False


class WebhookSettings(Settings):
    webhook_url: str
    webhook_secret: str | None = None

    class Config:
        case_sensitive = False
