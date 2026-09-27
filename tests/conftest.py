import pytest
from application.payments import PaymentsService
from application.rates import RatesService
from application.subscriptions.service import SubscriptionsTgBotService
from bootstrap import Container, create_container
from config.settings import Settings
from infra.xui_vpn.shared.factory import create_xui_vpn
from logs import config_logger
from presentation.bot.shared import loader


def pytest_addoption(parser):
    parser.addoption('--integration', action='store_true', default=False,
                     help='Запускать тесты, которые ходят в реальные сервисы')


def pytest_collection_modifyitems(config, items):
    # Всё вне tests/unit работает с боевыми 3x-ui / RollyPay (создаёт клиентов и платежи)
    skip = pytest.mark.skip(reason='integration: запуск с --integration')
    for item in items:
        if 'unit' not in item.path.parts:
            item.add_marker(pytest.mark.integration)
            if not config.getoption('--integration'):
                item.add_marker(skip)


@pytest.fixture(scope='session')
def set_logs_debug():
    config_logger('DEBUG')


@pytest.fixture
def settings():
    return Settings(_env_file=r'C:\Users\Пользователь\PycharmProjects\vpnbot_muxa\.env', _env_file_encoding='utf-8')


@pytest.fixture
def container(settings):
    return create_container(bot=loader.create_bot(settings.bot_token),
                            settings=settings)

@pytest.fixture
def xui_vpn(settings):
    return create_xui_vpn(
        api_key=settings.xui_api_key,
        base_url=settings.xui_api_url,
        sub_base_url=settings.xui_sub_base_url
    )


@pytest.fixture
def subs_service(xui_vpn):
    return SubscriptionsTgBotService(vpn_client=xui_vpn, rates=RatesService())


@pytest.fixture
def payment_service(container) -> PaymentsService:
    return container.payments()
