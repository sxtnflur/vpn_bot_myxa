import datetime

from domain.rates.sub_rate import SubRate


class RatesService:
    def __init__(self) -> None:
        self._rates: dict[int, SubRate] = {
            1: SubRate(
                id=1,
                name='LTE для телефона - 200 руб',
                price=200,
                protocol='!wireguard',
                sub_td=datetime.timedelta(days=30)
            ),

            2: SubRate(
                id=2,
                name='WIFI для роутера - 500 руб',
                price=500,
                protocol='wireguard',
                sub_td=datetime.timedelta(days=30)
            )
        }

    def get_rate(self, rate_id: int) -> SubRate:
        return self._rates[rate_id]

    def get_rates(self) -> list[SubRate]:
        return list(self._rates.values())
