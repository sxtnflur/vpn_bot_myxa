from infra.xui_vpn.shared.schemas import ClientPayload
from infra.xui_vpn.shared.xui_vpn import XUIVPN
from py3xui.async_api import AsyncClientApi


async def test_update_client(xui_vpn):
    await xui_vpn.clients.update(
        email='1304563494',
        client=ClientPayload(email='1304563494', reset_day=1, tg_id=1304563494)
    )


async def test_get_clients_list(xui_vpn: XUIVPN):
    result = await xui_vpn.clients.list(
        page=1, page_size=10
    )
    for row in result.items:
        client = await xui_vpn.clients.get(row.email)
        print(f'{client=}')
        assert client.client.email == row.email
        assert client.client.enable == row.enable
        assert client.client.expiry_time == row.expiry_time
        assert client.client.limit_ip == row.limit_ip


async def test_get_clients_by_tg_id(xui_vpn: XUIVPN):
    result = await xui_vpn.clients.list(
        page=1, page_size=10
    )
    tg_ids = {row.email: (await xui_vpn.clients.get(row.email)).client.telegram_id for row in result.items}
    for email, tg_id in tg_ids.items():
        if not tg_id:
            continue
        clients = await xui_vpn.clients.get_by_tg_id(tg_id)
        print(f'{clients=}')
        assert any(c.client.email == email for c in clients)


async def test_add_client(xui_vpn: XUIVPN):
    await xui_vpn.clients.add(
        ClientPayload(
            email=str(1304563494),
            tg_id=1304563494,
            comment='test user'
        )
    )


async def test_inbounds(xui_vpn):
    result = await xui_vpn.inbounds.list_slim()
    for inbound in result:
        print(f'{inbound=}')


async def test_get_links(xui_vpn):
    links = await xui_vpn.clients.links(sub_id='8c39c8ba-aeb7-4b6b-a51b-8751bd414038')
    print(f'{links=}')


async def test_get_client(xui_vpn):
    res = await xui_vpn.clients.get_by_tg_id(1304563494)
    print(f'{res=}')


async def test_get_traffic(xui_vpn, settings):
    client = AsyncClientApi(
        host=settings.xui_api_url,
        token=settings.xui_api_key
    )
    traffic = await client.get_traffic_by_id('7a3bfc89-0142-4d2d-81ef-cfa2695a84e8')
    print(f'{traffic=}')
    print(
        await xui_vpn.clients.traffic('AAZZHH')
    )
    # 53687091200