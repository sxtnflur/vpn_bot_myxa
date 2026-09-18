import pytest
from application.subscriptions.service import SubscriptionsTgBotService
from config.settings import Settings
from infra.xui_vpn.shared.factory import create_xui_vpn
from logs import config_logger


@pytest.fixture(scope='session')
def set_logs_debug():
    config_logger('DEBUG')


@pytest.fixture
def settings():
    return Settings(_env_file=r'C:\Users\Пользователь\PycharmProjects\vpnbot_muxa\.env', _env_file_encoding='utf-8')


@pytest.fixture
def xui_vpn(settings):
    return create_xui_vpn(
        api_key=settings.xui_api_key,
        base_url=settings.xui_api_url,
        sub_base_url=settings.xui_sub_base_url
    )


@pytest.fixture
def subs_service(xui_vpn):
    return SubscriptionsTgBotService(vpn_client=xui_vpn)