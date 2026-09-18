import datetime


async def test_add_subscription(subs_service):
    telegram_id = 1304563494

    expire_at = datetime.datetime.utcnow() + datetime.timedelta(days=1)
    expire_at = expire_at.replace(microsecond=(expire_at.microsecond // 1000) * 1000)

    expire_in = datetime.timedelta(days=1)

    result = await subs_service.add_subscription(
        telegram_id=telegram_id,
        full_name='Тему Бабрусько',
        username='sheggy_love',
        expire_in=expire_in
    )

    if not result.created:
        user = await subs_service.get_subscription(telegram_id)

        result = await subs_service.add_subscription(
            telegram_id=telegram_id,
            full_name='Тему Бабрусько',
            username='sheggy_love',
            expire_in=expire_in
        )

        assert result.created is False

        upd_user = await subs_service.get_subscription(telegram_id)

        assert (user.expire_at + expire_in) == upd_user.expire_at

    else:
        user = await subs_service.get_subscription(telegram_id)

        assert (user.expire_at + expire_in) == user.expire_at


async def test_get_sub_links(subs_service):
    sub_links = await subs_service.get_subscription_links(1304563494)
    for link in sub_links:
        print(link)
