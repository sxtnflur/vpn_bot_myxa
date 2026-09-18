import datetime

from pydantic.v1 import BaseSettings


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

    tz: datetime.timedelta = datetime.timedelta(hours=3)

    class Config:
        case_sensitive = False
