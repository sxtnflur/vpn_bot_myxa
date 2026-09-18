from infra.client.session.aiohttp import AiohttpSession
from infra.xui_vpn.shared.xui_vpn import XUIVPN


def create_xui_vpn(base_url: str, api_key: str, sub_base_url: str):
    return XUIVPN(
        base_url=base_url,
        api_key=api_key,
        session=AiohttpSession(
                headers={'Authorization': f'Bearer {api_key}'}
            ),
        sub_base_url=sub_base_url
    )
